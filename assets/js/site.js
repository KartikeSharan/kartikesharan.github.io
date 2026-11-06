/* Kartike Sharan: portfolio scripts
   1. Solder mask colour picker (remembered in this browser only)
   2. Traces on the home page board, routed from the J1 connector to each part
   3. Copper layer viewer on the flight controller page */
(function () {
  'use strict';
  var root = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. Solder mask picker ---------- */
  function setMask(name) {
    if (name === 'green') root.removeAttribute('data-mask');
    else root.setAttribute('data-mask', name);
    try { localStorage.setItem('mask', name); } catch (e) { /* storage unavailable: still works for this page */ }
    document.querySelectorAll('.mask-picker button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.mask === name));
    });
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', getComputedStyle(root).getPropertyValue('--mask').trim());
  }
  var current = root.getAttribute('data-mask') || 'green';
  document.querySelectorAll('.mask-picker button').forEach(function (b) {
    b.setAttribute('aria-pressed', String(b.dataset.mask === current));
    b.addEventListener('click', function () { setMask(b.dataset.mask); });
  });

  /* ---------- 2. Traces on the board ---------- */
  var board = document.querySelector('.board');
  var svg = board && board.querySelector('.traces');
  var led = board && board.querySelector('.led');
  var NS = 'http://www.w3.org/2000/svg';

  // Turn a list of Manhattan points into a path with 45-degree chamfered corners
  function chamfered(points, c) {
    var d = 'M' + points[0][0] + ',' + points[0][1];
    for (var i = 1; i < points.length - 1; i++) {
      var p0 = points[i - 1], p1 = points[i], p2 = points[i + 1];
      var inLen = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
      var outLen = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]);
      var k = Math.min(c, inLen / 2, outLen / 2);
      if (k < 1) { d += ' L' + p1[0] + ',' + p1[1]; continue; }
      var a = [p1[0] - (p1[0] - p0[0]) / inLen * k, p1[1] - (p1[1] - p0[1]) / inLen * k];
      var b = [p1[0] + (p2[0] - p1[0]) / outLen * k, p1[1] + (p2[1] - p1[1]) / outLen * k];
      d += ' L' + a[0].toFixed(1) + ',' + a[1].toFixed(1) + ' L' + b[0].toFixed(1) + ',' + b[1].toFixed(1);
    }
    var last = points[points.length - 1];
    return d + ' L' + last[0] + ',' + last[1];
  }

  function route(animate) {
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var box = board.getBoundingClientRect();
    var rel = function (r) { return { l: r.left - box.left, t: r.top - box.top, r: r.right - box.left, b: r.bottom - box.top, w: r.width, h: r.height }; };
    // start from the lowest pad on J1 (they wrap onto two lines on a phone)
    var pads = Array.prototype.slice.call(board.querySelectorAll('.connector .pad-link'));
    var j1 = pads.reduce(function (best, p) { return !best || p.getBoundingClientRect().bottom > best.getBoundingClientRect().bottom + 2 ? p : best; }, null);
    var parts = Array.prototype.slice.call(board.querySelectorAll('.part .fp'));
    if (!j1 || !parts.length) return;
    var narrow = window.innerWidth <= 720;
    var j = rel(j1.getBoundingClientRect());
    var start = [Math.round(j.l + 18), Math.round(j.b)];
    var rects = parts.map(function (p) { return rel(p.getBoundingClientRect()); });
    var spineX = Math.round(Math.min.apply(null, rects.map(function (r) { return r.l; })) - (narrow ? 26 : 34));
    var rowTops = [];
    rects.forEach(function (r) { if (!rowTops.some(function (t) { return Math.abs(t - r.t) < 8; })) rowTops.push(r.t); });
    rowTops.sort(function (a, b) { return a - b; });
    var prevBottom = start[1];
    var busYs = rowTops.map(function (t, i) {
      var above = i === 0 ? prevBottom : Math.max.apply(null, rects.filter(function (r) { return Math.abs(r.t - rowTops[i - 1]) < 8; }).map(function (r) { return r.b; }));
      return Math.round(above + (t - above) * (i === 0 ? 0.55 : 0.5) - 6);
    });
    var stroke = narrow ? 3 : 4;
    var paths = [];
    rects.forEach(function (r, i) {
      var row = rowTops.findIndex(function (t) { return Math.abs(t - r.t) < 8; });
      var busY = busYs[row];
      var padX = Math.round(r.l - (narrow ? 9 : 11));
      var padY = Math.round(r.t + 26);
      // Row 0 parts hang straight off the first bus; later rows go down the spine on the left
      var pts = row === 0
        ? [start, [start[0], busYs[0]], [padX, busYs[0]], [padX, padY]]
        : [start, [start[0], busYs[0]], [spineX, busYs[0]], [spineX, busY], [padX, busY], [padX, padY]];
      // drop zero-length segments
      pts = pts.filter(function (p, k) { return k === 0 || p[0] !== pts[k - 1][0] || p[1] !== pts[k - 1][1]; });
      var path = document.createElementNS(NS, 'path');
      path.setAttribute('d', chamfered(pts, narrow ? 8 : 12));
      path.setAttribute('stroke-width', stroke);
      path.dataset.part = String(i);
      svg.appendChild(path);
      var via = document.createElementNS(NS, 'circle');
      via.setAttribute('class', 'via');
      via.setAttribute('cx', padX); via.setAttribute('cy', busY); via.setAttribute('r', narrow ? 4 : 5);
      svg.appendChild(via);
      paths.push({ path: path, via: via, order: i });
    });
    var startVia = document.createElementNS(NS, 'circle');
    startVia.setAttribute('class', 'via');
    startVia.setAttribute('cx', start[0]); startVia.setAttribute('cy', start[1] + 4); startVia.setAttribute('r', narrow ? 4 : 5);
    svg.appendChild(startVia);

    if (animate && !reduceMotion) {
      paths.forEach(function (p) {
        var len = Math.ceil(p.path.getTotalLength());
        p.path.style.setProperty('--len', len);
        p.path.style.setProperty('--delay', (p.order * 0.12) + 's');
        p.via.style.setProperty('--delay', (0.6 + p.order * 0.12) + 's');
      });
      svg.classList.add('drawing');
      var total = 900 + paths.length * 120;
      window.setTimeout(function () { if (led) led.classList.add('on'); }, total);
    } else {
      svg.classList.remove('drawing');
      if (led) led.classList.add('on');
    }
  }

  if (board && svg) {
    var firstDraw = true;
    var draw = function () { route(firstDraw); firstDraw = false; };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw); else window.addEventListener('load', draw);
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(function () { route(false); }, 120); });
    board.querySelectorAll('.part .fp').forEach(function (fp, i) {
      var on = function () { var p = svg.querySelector('path[data-part="' + i + '"]'); if (p) { p.classList.add('hot'); svg.appendChild(p); } };
      var off = function () { var p = svg.querySelector('path[data-part="' + i + '"]'); if (p) p.classList.remove('hot'); };
      fp.addEventListener('mouseenter', on); fp.addEventListener('mouseleave', off);
      fp.addEventListener('focus', on); fp.addEventListener('blur', off);
    });
  }

  /* ---------- 3. Copper layer viewer ---------- */
  var viewer = document.querySelector('.layers');
  if (viewer) {
    var layers = viewer.querySelectorAll('.stack .layer');
    var buttons = viewer.querySelectorAll('.layer-btns button');
    var note = viewer.querySelector('.layer-note');
    var show = function (key) {
      layers.forEach(function (l) {
        var k = l.dataset.layer;
        l.classList.toggle('on', key === 'all' ? (k === 'L1' || k === 'silk') : k === key);
        l.classList.toggle('dim', key === 'all' && k !== 'L1' && k !== 'silk');
      });
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.layer === key)); });
      var active = viewer.querySelector('.layer-btns button[data-layer="' + key + '"]');
      if (note && active) note.textContent = active.dataset.note || '';
    };
    buttons.forEach(function (b) { b.addEventListener('click', function () { show(b.dataset.layer); }); });
    show('all');
  }
})();
