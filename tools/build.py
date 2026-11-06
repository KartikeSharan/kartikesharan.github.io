"""Builds the static site: index.html, projects/*.html and 404.html.

Run from the repository root:  python3 tools/build.py
Everything is plain HTML and CSS afterwards, so GitHub Pages serves the
output as it is (.nojekyll turns off Jekyll). Edit the text here, rebuild,
then commit the generated files as well.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kartikesharan.github.io'
CODE = 'https://github.com/KartikeSharan/engineering-projects/tree/main/'
REV = 'Rev 2026.11'

EMAIL = 'KartikeSharan07@gmail.com'
LINKEDIN = 'https://www.linkedin.com/in/kartike-sharan/'
GITHUB = 'https://github.com/KartikeSharan'


def entities(s):
    """Write an address as HTML character references (a light deterrent to scrapers)."""
    return ''.join(f'&#{ord(c)};' for c in s)


def svg(name):
    """Inline an SVG from assets/fig so its colours follow the page's CSS variables."""
    s = open(os.path.join(ROOT, 'assets', 'fig', name)).read()
    s = re.sub(r'<\?xml[^>]*>\s*', '', s)
    s = re.sub(r'<!DOCTYPE[^>]*>\s*', '', s)
    s = re.sub(r'<metadata>.*?</metadata>\s*', '', s, flags=re.S)
    # (url() inside a custom property resolves against the stylesheet that uses it, hence root-relative paths for the layer masks)
    # keep the viewBox, drop fixed sizes so the figure scales with its frame
    s = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r'\1', s, count=1)
    s = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r'\1', s, count=1)
    return s.strip()


MASKS = [('green', '#123f2a', 'Green'), ('black', '#1b1c1e', 'Matte black'), ('blue', '#0f2f5c', 'Blue'),
         ('purple', '#3a1d5c', 'Purple'), ('white', '#f3f3ee', 'White')]


def head(title, desc, prefix, path, image='assets/img/og.png'):
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Kartike Sharan">
<meta name="theme-color" content="#123f2a">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/{path}">
<meta property="og:image" content="{SITE}/{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{prefix}assets/fonts/b612-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{prefix}assets/fonts/atkinson-hyperlegible-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/css/site.css">
<script>try{{var m=localStorage.getItem('mask');if(m&&m!=='green')document.documentElement.setAttribute('data-mask',m);}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


def connector(label=True):
    ref = '<span class="ref" aria-hidden="true">J1</span>' if label else ''
    return f'''<div class="connector">
  {ref}
  <a class="pad-link" href="mailto:{entities(EMAIL)}">Email</a>
  <a class="pad-link" href="{LINKEDIN}" rel="me">LinkedIn</a>
  <a class="pad-link" href="{GITHUB}" rel="me">GitHub</a>
</div>'''


def footer(prefix):
    swatches = '\n'.join(
        f'      <button type="button" data-mask="{k}" style="--sw:{c}" aria-pressed="{str(k == "green").lower()}"><span class="label">{n}</span></button>'
        for k, c, n in MASKS)
    return f'''<footer class="foot">
  <div class="wrap">
    <div>
      <h2>Get in touch</h2>
      <p class="muted">The quickest way to reach me is email. I'm free for an internship across summer 2027.</p>
      {connector(False)}
      <small>{REV}. Board renders are made from my Gerber files. Hosted on GitHub Pages.</small>
    </div>
    <fieldset class="mask-picker">
      <legend>Solder mask colour</legend>
      <div class="swatches">
{swatches}
      </div>
    </fieldset>
  </div>
</footer>
<script src="{prefix}assets/js/site.js" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------- projects

PROJECTS = []   # filled below, in reading order


def project(slug, ref, title, summary, facts, body, links, desc=None):
    PROJECTS.append(dict(slug=slug, ref=ref, title=title, summary=summary, facts=facts,
                         body=body, links=links, desc=desc or summary))


def fig(src, alt, caption, n, paper=False, cls='', link=None):
    frame = 'frame paper' if paper else 'frame'
    img = f'<img src="../{src}" alt="{alt}" loading="lazy">'
    if link:
        img = f'<a href="../{link}">{img}</a>'
    return f'''<figure class="fig {cls}">
  <div class="{frame}">{img}</div>
  <figcaption><b>Figure {n}.</b> {caption}</figcaption>
</figure>'''


def fig_svg(name, caption, n, scroll=False, cls=''):
    frame = 'frame scroll' if scroll else 'frame'
    return f'''<figure class="fig {cls}">
  <div class="{frame}">{svg(name)}</div>
  <figcaption><b>Figure {n}.</b> {caption}</figcaption>
</figure>'''


LAYERS = [
    ('L1', 'L1_top', 'Top copper', 'Parts, short routes and the BGA pads.'),
    ('L2', 'L2_in1', 'Inner 1', 'Signal routing fanned out from the BGA.'),
    ('L3', 'L3_in2', 'Inner 2', 'A solid copper plane across the board.'),
    ('L4', 'L4_in3', 'Inner 3', 'A bus of parallel signals running to the header along the bottom edge.'),
    ('L5', 'L5_in4', 'Inner 4', 'More signal routing from the BGA.'),
    ('L6', 'L6_bottom', 'Bottom copper', 'Almost empty: only through-hole pads.'),
]


def layer_viewer():
    stack = '\n'.join(
        f'    <div class="layer" data-layer="{k}" style="--src:url(/assets/img/fc-layers/{f}.png)"></div>'
        for k, f, _, _ in LAYERS)
    stack += '\n    <div class="layer silk" data-layer="silk" style="--src:url(/assets/img/fc-layers/silk_top.png)"></div>'
    btns = ['    <button type="button" data-layer="all" data-note="Top copper and silkscreen, with the inner layers faintly behind." aria-pressed="true"><span class="ref">All</span><span>Top side</span></button>']
    for k, f, name, note in LAYERS:
        btns.append(f'    <button type="button" data-layer="{k}" data-note="{note}" aria-pressed="false"><span class="ref">{k}</span><span>{name}</span></button>')
    return f'''<div class="layers">
  <div class="stack" role="img" aria-label="Copper layers of the flight controller, one at a time">
{stack}
  </div>
  <div>
    <div class="layer-btns" aria-label="Choose a copper layer">
{chr(10).join(btns)}
    </div>
    <p class="layer-note muted" aria-live="polite"></p>
  </div>
</div>'''


project(
    'flight-controller', 'U1', 'Drone flight controller',
    'PCB layout of a six-layer drone flight controller for Atreides Industries, an early-stage drone start-up.',
    [('Role', 'PCB layout, alongside the schematic engineer'),
     ('Where', 'Atreides Industries (voluntary role)'),
     ('When', 'Jun to Nov 2025'),
     ('Board', 'Six layers, 59.6 × 66.6 mm, impedance-controlled stack-up'),
     ('Main parts', 'STM32H743 (169-ball BGA, 0.5 mm pitch), BMI323 IMU, BMM350 magnetometer, BME280 pressure sensor, USB-C'),
     ('Tools', 'KiCad')],
    f'''
<section>
<h2>The board</h2>
<div class="prose">
<p>This is the flight controller for the start-up's drone: the board that reads the motion sensors and runs the flight software. It's built around an STM32H743 microcontroller in a 169-ball BGA package with a 0.5 mm ball pitch, with a BMI323 inertial measurement unit, a BMM350 magnetometer, a BME280 pressure sensor, a 16 MHz crystal and a USB-C connector.</p>
</div>
{fig('assets/img/fc-top.webp', 'Rendered top side of the flight controller, showing the BGA microcontroller, sensors, USB-C connector and the header along the bottom edge', 'Top side, rendered from the Gerber files that went to fabrication.', 1, cls='narrow')}
</section>

<section>
<h2>What I did</h2>
<div class="prose">
<p>I owned the PCB layout. The circuit itself came from the company's schematic engineer, and I worked alongside them to turn it into a board that could be made.</p>
<ul>
<li>Checked every footprint against the manufacturer's drawing.</li>
<li>Ran the electrical and design rule checks (ERC and DRC) and resolved every violation.</li>
<li>Where the choice of part was mine, compared the options on performance, size and cost.</li>
<li>Kept the board's interfaces compatible with what the mechanical and electronics engineers were building around it.</li>
<li>Dealt with suppliers on procurement.</li>
<li>Delivered the manufacture-ready files: Gerbers, drill files, the bill of materials and pick-and-place data.</li>
</ul>
</div>
</section>

<section>
<h2>Inside the board</h2>
<div class="prose">
<p>The board has six copper layers in an impedance-controlled stack-up. Most of the parts and short routes sit on the top layer, inner layer 2 is a solid copper plane, and the other inner layers carry most of the signal routing. 257 blind vias run from the top layer down to one of the inner layers, the usual way to escape-route a 0.5 mm-pitch BGA, alongside 13 through-holes and 4 slots.</p>
<p>Pick a layer to see it on its own.</p>
</div>
{layer_viewer()}
</section>

<section>
<h2>Also at Atreides: repairing ESCs</h2>
<div class="prose">
<p>A batch of electronic speed controllers had burnt tracks and excess solder. I worked out that the damage came from earlier rework rather than failure in service, so the units could be saved. I desoldered the damaged areas, cleaned them with isopropyl alcohol, bridged the burnt tracks with wire links and checked continuity before returning them to spares.</p>
</div>
</section>

<section>
<h2>What I took from it</h2>
<div class="prose">
<p>Joining a start-up this early showed me how a small company actually works: everyone pitches in and takes on far more than their job title. Working directly with the CEO and seeing what he does day to day was the most valuable part.</p>
</div>
</section>
''',
    [('Design files on GitHub', CODE + 'atreides-flight-controller')])

project(
    'drone-kit', 'U2', 'Educational drone kit',
    'A solder-free, modular drone kit that secondary-school pupils assemble and programme themselves. I proposed it for the society\'s schools outreach and designed its electronics.',
    [('Role', 'Proposed the kit; designed the electronics'),
     ('Where', 'Glasgow University Drones, as Head of Electronics'),
     ('When', '2025 to 2026'),
     ('Board', 'Two layers, 70.6 × 70.6 mm'),
     ('Main parts', 'ESP32-C3 module, ICM-42670-P IMU, two DRV8833 dual H-bridges, TPS63001 buck-boost, BQ24074 charger'),
     ('Status', 'First boards fabricated; assembly and testing next')],
    f'''
<section>
<h2>Why a kit</h2>
<div class="prose">
<p>The society runs outreach with secondary schools. I proposed a drone that pupils could build and program themselves without a soldering iron, and that could be taken apart and reused by the next group. It's the society's own project; the University isn't involved.</p>
</div>
{fig('assets/img/devkit-top.webp', 'Rendered top side of the drone kit board, with the ESP32-C3 module at the top, motor connectors on the left and right edges and the charger and power circuitry at the bottom', 'Top side of the kit board, rendered from its Gerber files.', 1, cls='narrow')}
</section>

<section>
<h2>Design decisions</h2>
<div class="prose">
<ul>
<li><strong>No soldering for pupils.</strong> JST connectors on the battery and motor outputs, and a USB-C receptacle for both power and programming.</li>
<li><strong>A steady 3.3 V rail.</strong> A TPS63001 buck-boost converter holds 3.3 V across the LiPo battery's full discharge range. A diode-OR power path takes power from USB or the battery, with reverse-polarity protection, and a BQ24074 charges the battery.</li>
<li><strong>Four motors from two chips.</strong> Two DRV8833 dual H-bridges drive the four motors.</li>
<li><strong>Sensors that fit the pins.</strong> I ruled out sensors whose interfaces the microcontroller's free pins couldn't support, and presented the evidence to the team. The kit uses an ICM-42670-P IMU.</li>
<li><strong>Safe for a classroom.</strong> Low-voltage rechargeable batteries and propeller guards, with the principles of the BS EN 71 toy-safety standard considered.</li>
<li><strong>Fits the frame.</strong> I agreed the board's size and the position of parts, including the battery, with the mechanical team designing the chassis.</li>
</ul>
</div>
{fig('assets/img/devkit-schematic.webp', 'Full schematic of the drone kit board', 'The kit\'s schematic. Select it to open the full-size image.', 2, paper=True, link='assets/img/devkit-schematic.webp')}
</section>

<section>
<h2>Running the project</h2>
<div class="prose">
<p>The team compared candidate parts against fixed criteria: compatibility, communication protocol, reliability, function, footprint and cost. I put together a budget of about £500 with a contingency, which was approved, and compared quotes from several PCB manufacturers. Once the design passed ERC and DRC I released the Gerbers and handed ordering to the team.</p>
<p>As Head of Electronics I lead a team of three to five engineers, approve every schematic and PCB layout before it's released, and run KiCad workshops for members.</p>
</div>
</section>
''',
    [('Design files on GitHub', CODE + 'gud-drone-devkit')])

MUTATIONS = [
    ('ADD computes OR', False, True), ('ADD computes XOR', False, True), ('SUB swaps its operands', True, True),
    ('AND computes OR', False, True), ('OR computes XOR', False, True), ('Shift left goes right', False, True),
    ('Shift right goes left', False, True), ('MOV passes A instead of B', True, True)]


def mutation_table():
    rows = '\n'.join(
        f'<tr><td>{n}</td><td class="{"yes" if a else ""}">{"Caught" if a else "Missed"}</td><td class="{"yes" if b else ""}">{"Caught" if b else "Missed"}</td></tr>'
        for n, a, b in MUTATIONS)
    return f'''<div class="table-wrap"><table class="data">
<caption class="muted" style="text-align:left;padding-bottom:10px">Bugs deliberately put into the ALU one at a time, and whether each test noticed.</caption>
<thead><tr><th scope="col">Injected bug</th><th scope="col">Original test</th><th scope="col">New testbench</th></tr></thead>
<tbody>
{rows}
</tbody></table></div>'''


project(
    'risc16-cpu', 'U3', 'RISC16 processor',
    'A 16-bit processor in Verilog, built on a course framework at UESTC. After the course I reviewed it, found seven problems and wrote a revised version with a self-checking testbench.',
    [('Course', 'Digital Logic Design, Glasgow College UESTC (2026)'),
     ('Instruction set', '16-bit: 4-bit opcode, two 2-bit register fields, 8-bit immediate'),
     ('Tools', 'Verilog, Vivado, FPGA board'),
     ('Review', 'November 2026, with help from an AI assistant'),
     ('Result', 'The new testbench catches 8 of 8 injected bugs; the original test caught 2')],
    f'''
<section>
<h2>The design</h2>
<div class="prose">
<p>The processor has four 16-bit registers and a datapath made of a register file, an operand multiplexer, a seven-operation ALU and a program counter. A multi-cycle control unit steps each instruction through Fetch, Decode, Execute and Write back, and a handshake from the ALU holds Execute until the result is ready.</p>
<p>The course supplied the module framework and, from Lab 4 on, a completed control unit. My parts of the submitted design were the ALU's operations, completing the AND and OR branches of the control FSM, the system testbench and an 11-instruction test program in ROM, plus the design report. I simulated it in Vivado and ran its modules on an FPGA board.</p>
</div>
{fig('assets/img/cpu-rtl-datapath.webp', 'Vivado RTL schematic of the processor datapath', 'The datapath as Vivado elaborated it, from the course version.', 1, paper=True)}
</section>

<section>
<h2>Reviewing it after the course</h2>
<div class="prose">
<p>In November 2026, with help from an AI assistant, I rebuilt the submitted design from my report, re-simulated it and went through it line by line. It reproduced my report's results exactly, and it also had problems:</p>
<ul>
<li>The test program couldn't catch ALU bugs. Most operands were zero, AND never ran and results were checked by eye.</li>
<li>Three instructions in the course's own instruction set (move between registers, add between registers, AND with an immediate) had no decode case, so the control FSM got stuck in Decode.</li>
<li>No instruction selected the two shift operations, so the processor could only use five of the ALU's seven.</li>
<li>My report misread ADD: opcode 0010 is add-immediate by design, and the program added an immediate of zero.</li>
<li>The testbench released reset exactly on a rising clock edge, a race that can skip the first instruction.</li>
<li>Synthesis inferred three latches: one in the control unit and two in the register file.</li>
<li>My report said the test program exercised every implemented opcode, but AND and the shifts never ran.</li>
</ul>
</div>
</section>

<section>
<h2>The revised version</h2>
<div class="prose">
<ul>
<li>Every documented instruction is decoded, plus new shift-left and shift-right instructions. An unknown opcode is treated as a no-op instead of hanging the processor.</li>
<li>No latches: every control output has a default, and the register file's read ports are a plain multiplexer.</li>
<li>A self-checking testbench runs a 15-instruction program against a reference model and checks the fetched instruction and all four registers after every instruction. It fails if any opcode never runs or if the control unit hangs.</li>
<li>GitHub Actions runs the testbench on every push.</li>
</ul>
</div>
{mutation_table()}
{fig_svg('cpu-wave.svg', 'The revised processor running its test program: F, D, E and W are the Fetch, Decode, Execute and Write back states. On a narrow screen, scroll sideways.', 2, scroll=True)}
</section>
''',
    [('Code and review on GitHub', CODE + 'risc16-cpu')])

project(
    'line-following-robot', 'U4', 'Line-following robot',
    'A Year 3 team design project: a robot that follows a line, detects obstacles and makes its own decisions. I lead the six-person team and own the firmware.',
    [('Team', 'Six students (Team 7), Team Design Project 3'),
     ('My role', 'Project lead and firmware'),
     ('When', 'Oct 2026 to now'),
     ('Microcontroller', 'NXP KL25Z (Arm Cortex-M0+, 48 MHz) on a FRDM-KL25Z board'),
     ('Motor driver', 'L298 dual H-bridge'),
     ('Status', 'Firmware builds; first drive at the interim demo by 20 Nov 2026')],
    f'''
<section>
<h2>Leading the team</h2>
<div class="prose">
<p>I planned the project on a Gantt chart and gave each stage a named lead: schematic, breadboard prototype, PCB design and build, software and final assembly. I chose the L298 dual H-bridge motor driver and split the electronics into three boards: power distribution (12 V, 5 V from a 7805 and 3.3 V from an LD1117), motor drive, and a breakout for the microcontroller.</p>
<p>While writing the wiring guide I noticed that the planned breakout left no free pins for the line sensors, and asked for the board's analogue header to be broken out before the PCB was made.</p>
</div>
{fig_svg('robot-block.svg', 'How the robot\'s electronics fit together.', 1, cls='chart')}
</section>

<section>
<h2>Firmware</h2>
<div class="prose">
<p>The firmware is register-level C with no operating system or Mbed layer, so every peripheral is set up directly from the reference manual.</p>
<ul>
<li>Motor control with 10 kHz PWM, ramping from stop to full speed over 250 ms, a 100 ms stop before reversing (the gearmotor's datasheet asks for it) and braking at zero speed.</li>
<li>A 1 ms SysTick timebase for timing, and UART debug output at 115200 baud.</li>
<li>Calibration and motor-test modes, and the interim route stored as a table of distances and turns.</li>
</ul>
<h3>Fail-safes</h3>
<ul>
<li>If the processor faults, the fault handler cuts both motors.</li>
<li>10 kΩ pull-down resistors hold the motor enables low while the microcontroller is in reset or being programmed, so the wheels can't start on their own.</li>
</ul>
<h3>Tooling for the team</h3>
<p>I wrote a Python tool that installs the compiler, builds the firmware, flashes the board through its USB drive, checks that programming succeeded and opens a serial monitor, all run from VS Code tasks, so anyone in the team can build and flash with one command.</p>
</div>
<div class="note"><p>The firmware builds but hasn't driven the robot yet, and its calibration values are placeholders. I'll update this page after the interim demo.</p></div>
</section>
''',
    [('Firmware and wiring guide on GitHub', CODE + 'tdp3-line-following-robot')])

project(
    'cold-chain-logger', 'U5', 'Cold-chain transport logger',
    'An STM32 logger that watches temperature and knocks during transport and raises an alarm when either goes out of range. A pair project for Embedded Processors at UESTC.',
    [('Team', 'Pair project with Elyas Omar'),
     ('Board', 'NUCLEO-L432KC (STM32L432KC, Arm Cortex-M4F)'),
     ('Sensors', 'TMP102 temperature (I2C), ADXL345 accelerometer (SPI)'),
     ('Tools', 'C++, Mbed OS 6, Keil Studio'),
     ('Module mark', 'Embedded Processors: 82%')],
    f'''
<section>
<h2>How it works</h2>
<div class="prose">
<p>Medicines and vaccines have to stay within a temperature range in transit, and a dropped box can damage them too. The logger sits idle until a button press starts a journey. It then reads both sensors every two seconds, sleeping in between, and logs every event. If the temperature leaves its range or the accelerometer sees a shock, it switches to an alert state: the red LED comes on and a 2 kHz tone beeps. Three good temperature readings in a row return it to normal, and a second button press ends the journey and prints the full event log over serial.</p>
<p>The design follows the WHO's 2 to 8 °C cold-chain range for vaccines and a 2 g shock limit. The build we submitted has its limits set to 20 to 30 °C and 1.2 g.</p>
</div>
{fig_svg('logger-states.svg', 'The logger\'s three states and what moves it between them.', 1, cls='chart')}
{fig_svg('logger-block.svg', 'Hardware: two sensors on separate buses, with the button on an interrupt and the buzzer on PWM.', 2, cls='chart')}
</section>

<section>
<h2>A fault worth remembering</h2>
<div class="prose">
<p>Partway through, both sensors stopped responding at once. I tested each one on its own, which pointed to the board rather than our code: on the NUCLEO-L432KC, solder bridges SB16 and SB18 join two of the pins we were using for SPI to the I2C pins. Moving the SPI bus to free pins fixed it.</p>
</div>
</section>

<section>
<h2>Code structure</h2>
<div class="prose">
<p>The code is split into modules, each with its own header: the main state machine, a driver for each sensor, and the event log. The button only sets a flag inside its interrupt, and the main loop does the work, because printing and sleeping aren't safe inside an interrupt handler.</p>
</div>
</section>
''',
    [('Code on GitHub', CODE + 'stm32-embedded/cold-chain-logger')])

project(
    'stm32-labs', 'R1', 'STM32 lab programs',
    'Ten programs for the NUCLEO-L432KC from the Embedded Processors labs at UESTC: timers and PWM, an accelerometer over SPI and a temperature sensor over I2C.',
    [('Course', 'Embedded Processors, UESTC (2026); module mark 82%'),
     ('Board', 'NUCLEO-L432KC (Arm Cortex-M4F)'),
     ('Tools', 'C++, Mbed OS 6, Keil Studio'),
     ('Result', 'About 40 times lower sensor current using shutdown mode with interrupt-triggered readings')],
    '''
<section>
<h2>The programs</h2>
<div class="prose">
<p>Keil Studio Cloud closed when Arm ended Mbed, taking the original projects with it, so these were recovered from the code printed in my lab reports.</p>
</div>
<div class="table-wrap"><table class="data">
<thead><tr><th scope="col">Lab</th><th scope="col">Task</th><th scope="col">What it does</th></tr></thead>
<tbody>
<tr><td>2</td><td>2.4</td><td>A 1 kHz PWM output whose duty cycle a timer interrupt switches between 70% and 30% every two seconds, with an LED showing which.</td></tr>
<tr><td>3</td><td>2</td><td>Sets up the SPI bus for the ADXL345 accelerometer at a 2 MHz clock.</td></tr>
<tr><td>3</td><td>3</td><td>Reads all three axes from the ADXL345.</td></tr>
<tr><td>3</td><td>4</td><td>Drives LEDs from the accelerometer readings.</td></tr>
<tr><td>3</td><td>5</td><td>Eight LEDs show which way, and how far, the board is tilted on each axis.</td></tr>
<tr><td>4</td><td>1</td><td>Reads the TMP102 temperature sensor in continuous conversion mode.</td></tr>
<tr><td>4</td><td>2</td><td>Averages readings to reduce noise.</td></tr>
<tr><td>4</td><td>3</td><td>Puts the TMP102 into shutdown mode.</td></tr>
<tr><td>4</td><td>4</td><td>Compares the current drawn in continuous and shutdown modes.</td></tr>
<tr><td>4</td><td>5</td><td>Takes a one-shot reading each time a push-button interrupt fires.</td></tr>
</tbody></table></div>
<div class="prose">
<p>Measuring the current showed that keeping the sensor in shutdown mode and only waking it for a one-shot reading when needed cut its current by about 40 times.</p>
</div>
</section>

<section>
<h2>Looking back</h2>
<div class="prose">
<p>Recovering the code meant reading it again, and two things stood out:</p>
<ul>
<li>In Lab 4 Task 5 the program waits 20 ms after starting a one-shot conversion, but the TMP102 datasheet gives a typical conversion time of 26 ms, so a reading can return the previous result. Waiting 35 ms, or polling the one-shot bit, fixes it.</li>
<li>Temperatures between 0 and -1 °C would print without their minus sign, because the whole-number part is printed after a cast to int, which rounds towards zero.</li>
</ul>
</div>
</section>
''',
    [('Code on GitHub', CODE + 'stm32-embedded')])

project(
    'tcad-pn-junction', 'R2', 'Silicon p-n junction in Sentaurus TCAD',
    'Simulating a silicon p-n junction with and without recombination in Synopsys Sentaurus TCAD, and reading what the current-voltage curves show.',
    [('Course', 'Electronic Devices 3, University of Glasgow (Oct 2026)'),
     ('Tools', 'Synopsys Sentaurus Structure Editor and Sentaurus Device'),
     ('Device', 'Symmetric junction, 10<sup>17</sup> cm<sup>-3</sup> boron and phosphorus, 0.5 µm each side')],
    f'''
<section>
<h2>The simulation</h2>
<div class="prose">
<p>The junction was swept from 0 V to -1 V (reverse bias) and then up to +0.6 V (forward bias) on the p contact, with the n contact held at 0 V. I ran it twice: once with no recombination model, and once as an ideal junction with Shockley-Read-Hall (SRH) recombination only in the neutral regions. The command files started from course templates and I set the parameters, including the forward limit of 0.6 V.</p>
</div>
{fig('assets/img/tcad-structure.webp', 'Doping profile of the simulated junction: p-type on the left, n-type on the right, 0.5 micrometres each', 'The simulated structure: p-type and n-type silicon, 0.5 µm each.', 1, paper=True, cls='narrow')}
{fig_svg('tcad-iv.svg', 'Current against voltage for both runs, from my simulation output. The two curves overlap in forward bias.', 2, cls='chart')}
</section>

<section>
<h2>What the curves show</h2>
<div class="prose">
<ul>
<li>In forward bias the current rises by about one decade for every 60 mV between 0.3 V and 0.6 V, which is what an ideal diode (ideality factor 1) does at room temperature.</li>
<li>In reverse bias, adding SRH recombination in the neutral regions raises the leakage current at -1 V about 40 times, from 1.6 × 10<sup>-18</sup> to 6.3 × 10<sup>-17</sup> A/µm.</li>
</ul>
</div>
</section>
''',
    [('Simulation files on GitHub', CODE + 'tcad-pn-junction')])

project(
    'signal-processing', 'R3', 'Signal processing in Python',
    'Sampling, aliasing and AM modulation simulated in Python, with a discrete Fourier transform written from its definition and checked against NumPy\'s FFT.',
    [('Course', 'Communication Systems 3, University of Glasgow (Oct 2026)'),
     ('Tools', 'Python, NumPy, Matplotlib, Jupyter')],
    f'''
<section>
<h2>What the notebook does</h2>
<div class="prose">
<ul>
<li>Samples a 5 Hz sine at several rates, including below twice its frequency to show aliasing.</li>
<li>Generates an AM signal (a 5 Hz message on a 50 Hz carrier, sampled at 1 kHz), including over-modulation.</li>
<li>Implements the discrete Fourier transform from the lab sheet's definition and checks it against NumPy's FFT.</li>
<li>Explores spectral leakage with a sample count that isn't a whole number of cycles, a lower sample rate, and a carrier above half the sample rate.</li>
<li>Band-pass filters the AM signal in the frequency domain (carrier only, carrier with both sidebands, carrier with the upper sideband) and returns to the time domain with an inverse FFT.</li>
</ul>
</div>
<div class="fig-pair">
{fig('assets/img/dsp-task1.webp', 'Sine waves sampled at several rates, with aliasing at the lowest rate', 'Sampling a sine at different rates.', 1, paper=True)}
{fig('assets/img/dsp-task2.webp', 'AM signals with modulation index 0.5 and 1.5, showing over-modulation', 'AM with normal and over-modulation.', 2, paper=True)}
</div>
{fig('assets/img/dsp-task4.webp', 'Six spectra showing the effect of array length, sample rate and carrier frequency', 'Spectra under different sampling choices, including leakage.', 3, paper=True)}
{fig('assets/img/dsp-task5.webp', 'Frequency-domain band-pass filters and the resulting time-domain signals', 'Filtering the AM signal in the frequency domain.', 4, paper=True)}
</section>
''',
    [('Notebook on GitHub', CODE + 'comms-signal-processing-python')])

project(
    'ring-counter', 'R4', 'Ring counter on a MAX 10 FPGA',
    'Digital logic in Quartus on a DE10-Lite board: a ripple-carry adder driving a seven-segment display, a ripple counter and an 8-bit ring counter.',
    [('Course', 'Digital Electronics 2, University of Glasgow (2025)'),
     ('Board', 'Terasic DE10-Lite (Intel MAX 10 FPGA)'),
     ('Tools', 'VHDL, Quartus, Tektronix oscilloscope, signal generator')],
    f'''
<section>
<h2>The ring counter</h2>
<div class="prose">
<p>I converted a provided 8-bit shift register into a ring counter in Quartus's block editor by feeding its last output back to its serial input and parallel-loading 00000001. I checked reset and shifting in a waveform simulation before programming the board, assigned the pins, then clocked it from a push-button and from an external signal generator, checking the clock on an oscilloscope. The pattern repeats every eight clock cycles.</p>
</div>
{fig('assets/img/ring-simulation-waveform.webp', 'Quartus waveform simulation of the ring counter shifting a single 1 through eight outputs', 'Simulating the ring counter before programming the board.', 1, paper=True)}
{fig('assets/img/ring-fpga.webp', 'Lab bench with a signal generator and oscilloscope connected to the FPGA board', 'The bench set-up.', 2, cls='narrow')}
</section>
''',
    [('Report on GitHub', CODE + 'de2-vhdl-ring-counter')])

project(
    'year1-pcbs', 'R5', 'Year 1 circuit boards',
    'An electronic dice and a logic board, designed in OrCAD Capture and Allegro, then built and tested by hand.',
    [('Course', 'Engineering Skills 1, University of Glasgow (2024)'),
     ('Tools', 'OrCAD Capture, Allegro PCB Editor, bench supply, multimeter, soldering')],
    f'''
<section>
<h2>Electronic dice</h2>
<div class="prose">
<p>I designed the circuit, drew the schematic in OrCAD Capture, laid out a double-sided board in Allegro, then built and tested it myself. It uses a 74HC132 quad Schmitt NAND and a 74HC175 quad D flip-flop to light seven LEDs. Testing with a bench supply and multimeter for shorts and open circuits found some diodes placed the wrong way round, which I corrected.</p>
</div>
<div class="fig-pair">
{fig('assets/img/dice-schematic.webp', 'Schematic of the electronic dice', 'Dice schematic.', 1, paper=True)}
{fig('assets/img/dice-top-pcb.webp', 'Top copper layout of the electronic dice board', 'Dice board, top layer.', 2, paper=True)}
</div>
</section>

<section>
<h2>Logic board</h2>
<div class="prose">
<p>A 22-part board with 74HC14 Schmitt inverters, a 74HC164 shift register, 74HC86 XOR gates, seven LEDs and an LM2931 regulator. After testing the first board I re-routed more of the IC connections onto the bottom layer to reduce the board's complexity.</p>
</div>
<div class="fig-pair">
{fig('assets/img/logic-board-schematic.webp', 'Schematic of the logic board', 'Logic board schematic.', 3, paper=True)}
{fig('assets/img/logic-board-top-pcb.webp', 'Top copper layout of the logic board', 'Logic board, top layer.', 4, paper=True)}
</div>
</section>
''',
    [('Design files on GitHub', CODE + 'year1-pcb-design')])


def project_page(i, p):
    prev = PROJECTS[i - 1] if i > 0 else None
    nxt = PROJECTS[i + 1] if i + 1 < len(PROJECTS) else None
    facts = '\n'.join(f'  <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in p['facts'])
    links = '\n'.join(f'  <a class="pad-link" href="{u}">{t}</a>' for t, u in p['links'])
    pager = '<nav class="pager" aria-label="More projects">'
    pager += (f'<a href="{prev["slug"]}.html" rel="prev"><span>Previous</span>{prev["title"]}</a>' if prev else '<span></span>')
    pager += (f'<a href="{nxt["slug"]}.html" rel="next" style="text-align:right"><span>Next</span>{nxt["title"]}</a>' if nxt else '<a href="../index.html#projects"><span>Back to</span>All projects</a>')
    pager += '</nav>'
    title = f'{p["title"]}: Kartike Sharan'
    return head(title, p['desc'].replace('"', '&quot;'), '../', f'projects/{p["slug"]}.html') + f'''<header class="topbar">
  <div class="wrap">
    <a class="home" href="../index.html">Kartike Sharan</a>
    <nav aria-label="Site"><a href="../index.html#projects">All projects</a></nav>
  </div>
</header>
<main id="main" class="wrap">
<div class="doc-head">
  <span class="ref">{p["ref"]}</span>
  <h1>{p["title"]}</h1>
  <p class="summary">{p["summary"]}</p>
  <dl class="facts">
{facts}
  </dl>
</div>
<article class="doc">
{p["body"]}
<div class="links">
{links}
</div>
</article>
{pager}
</main>
''' + footer('../')


# ---------------------------------------------------------------- home page

FEATURED = [
    ('flight-controller', 'U1', 'big', 'Drone flight controller',
     'Layout of a six-layer drone flight controller for a start-up, built around a 169-ball STM32H7 with blind vias into the inner layers.',
     'KiCad', 'Industry, 2025', '<img src="assets/img/fc-top.webp" alt="" loading="eager">'),
    ('drone-kit', 'U2', 'big', 'Educational drone kit',
     'A solder-free drone kit that pupils assemble and programme themselves. I proposed it for the society\'s school outreach and designed the electronics.',
     'KiCad, ESP32-C3', 'Boards fabricated', '<img src="assets/img/devkit-top.webp" alt="" loading="eager">'),
    ('risc16-cpu', 'U3', '', 'RISC16 processor',
     'A 16-bit CPU in Verilog, then a review that found seven problems and a revised design with a self-checking testbench.',
     'Verilog, Vivado', 'Coursework and review', None),
    ('line-following-robot', 'U4', '', 'Line-following robot',
     'I lead a six-person team and write the firmware: register-level C on an Arm Cortex-M0+.',
     'C, Python', 'In progress', None),
    ('cold-chain-logger', 'U5', '', 'Cold-chain logger',
     'An STM32 logger that sounds an alarm when the temperature leaves its range or the package takes a knock.',
     'C++, Mbed OS, I2C, SPI', 'Pair project', None),
]
THUMB_SVG = {'risc16-cpu': 'cpu-wave-thumb.svg', 'line-following-robot': 'robot-block.svg',
             'cold-chain-logger': 'logger-states.svg'}


def part_html(slug, ref, size, title, line, tools, state, img):
    figure = img if img else svg(THUMB_SVG[slug]).replace('role="img"', 'aria-hidden="true"', 1)
    return f'''<div class="part {size}">
  <a class="fp" href="projects/{slug}.html">
    <span class="desig" aria-hidden="true">{ref}</span><span class="pin1" aria-hidden="true"></span>
    <figure>{figure}</figure>
    <div class="body">
      <h3>{title}</h3>
      <p>{line}</p>
      <p class="tools">{tools}</p>
      <span class="state">{state}</span>
    </div>
  </a>
</div>'''


MORE = [
    ('R1', 'STM32 lab programs', 'projects/stm32-labs.html',
     'Timers and PWM, an accelerometer over SPI and a temperature sensor over I2C, including shutdown mode.'),
    ('R2', 'p-n junction in Sentaurus TCAD', 'projects/tcad-pn-junction.html',
     'A silicon junction simulated with and without recombination, and what the current curves show.'),
    ('R3', 'Signal processing in Python', 'projects/signal-processing.html',
     'Aliasing, AM modulation and a DFT written from its definition, checked against NumPy\'s FFT.'),
    ('R4', 'Ring counter on a MAX 10 FPGA', 'projects/ring-counter.html',
     'Logic built in Quartus, simulated, then clocked on the board from a push-button and a signal generator.'),
    ('R5', 'Year 1 circuit boards', 'projects/year1-pcbs.html',
     'An electronic dice and a logic board, designed in OrCAD and Allegro, then built and tested by hand.'),
    ('R6', 'Quine-McCluskey minimiser', CODE + 'quine-mccluskey',
     'Boolean logic minimisation with don\'t-care terms, in Python. Programming 2 coursework.'),
    ('R7', 'Society flight controller', CODE + 'gud-flight-controller',
     'An earlier Glasgow University Drones flight controller schematic, modelled on the Pixhawk connector standard.'),
]

EXPERIENCE = [
    ('Engineering and Maintenance Summer Placement', 'Sellafield Ltd, Cumbria', 'Jul to Sep 2026',
     'Rotations in remote robotics and distributed control systems (DCS) on a nuclear-licensed site. BPSS cleared.',
     ['Wrote precheck and runcheck logic in Taylor Control Language for a high-level waste plant modification on an ABB MOD 300 Advant DCS, so that normal running (one of four feed states) depends on a new air-sparge flow meter.',
      'Built an offline test environment and verified the logic before installation, catching earlier-stage errors for correction.',
      'Traced a steam-flow fault that was halting an evaporator to the 4–20 mA to 1–5 V conversion stage, and switched the live DCS to its backup controller under supervision. Flow was restored after the faulty hardware was replaced.',
      'Replaced controller and network cards on an operational MOD 300 DCS; wrote a software-switch operating-conditions report, issued to Operations Support, and revised an operator change-control procedure.',
      'Configured autonomous inspection routes for a Boston Dynamics Spot and designed structured tests of its AI anomaly detection; isolated a fleet-software data-transfer fault and debugged ROS 2 reference-frame errors.',
      'Proposed a client-task workflow for the robotics team, which was approved, and presented my placement to the Director of Maintenance.']),
    ('Vice President, and Head of Electronics since Sep 2025', 'Glasgow University Drones', 'Feb 2025 to now',
     None,
     ['Lead a team of three to five electronics engineers, with final approval on every schematic and PCB layout, and run KiCad workshops.',
      'Proposed and designed the society\'s <a href="projects/drone-kit.html">educational drone kit</a>.',
      'Electronics lead for the society\'s IMechE UAS Challenge entry: raised £1,820 in sponsorship and a University grant, and modelling mission energy for its 10 kg VTOL quadplane.',
      'Recruited more than ten new members and assigned project team leads.']),
    ('Electronic Engineer (voluntary)', 'Atreides Industries, drone start-up', 'Jun to Nov 2025',
     None,
     ['Owned the PCB layout of the company\'s <a href="projects/flight-controller.html">flight controller</a> alongside the schematic engineer.',
      'Repaired rework-damaged speed controllers back to spares stock.',
      'Dealt with suppliers on procurement, and with the mechanical and electronics engineers on interfaces.']),
    ('Student Representative', 'Year 3 Electronic and Electrical Engineering, University of Glasgow', '2026 to now',
     None,
     ['Collect the issues students in my year raise, take them to meetings and present them.',
      'Advocate for students to get their problems resolved.']),
    ('International Ambassador', 'James Watt School of Engineering', 'Feb 2026 to now',
     None,
     ['Presented to about 40 prospective exchange students in Chengdu, and now support two newly arrived exchange students.',
      'Helping the University build an exchange support programme for later cohorts.']),
    ('Maths and Physics Tutor', 'Self-employed', '2022 to now',
     None,
     ['Tutor students up to Advanced Higher: all ten of last year\'s students achieved an A or B, and 80% of those applying to university got their first choice.']),
    ('Co-founder and CEO', 'Kathode', '2026 to now',
     None,
     ['An early-stage start-up planning low-cost EV charging built into on-street parking, for streets of tenements with nowhere to charge.']),
]

GRADES = [
    ('Year 1, 2024 to 2025', [
        ('Electronic Engineering 1X', 20, 'A2'),
        ('Electronic Engineering 1Y', 20, 'A5'),
        ('Engineering Skills 1', 10, 'A4'),
        ('Materials 1', 10, 'A2'),
        ('Dynamics 1', 10, 'C3'),
        ('Engineering Mathematics 1', 40, 'A2'),
        ('Thermodynamics 1', 10, 'A2')]),
    ('Year 2, first semester, 2025', [
        ('Digital Electronics 2', 10, 'A2'),
        ('Electrical Circuits 2', 10, 'B1'),
        ('Power Electronics 2', 10, 'A5'),
        ('Introductory Programming 2', 10, 'A1'),
        ('Engineering Mathematics 2', 20, 'A2')]),
]

YEAR3_MODULES = ['Communication Systems 3', 'Control 3', 'Electromagnetic Compatibility 3', 'Electronic Circuit Design 3',
                 'Electronic Devices 3', 'Electronic System Design 3', 'Engineering Career Skills 3', 'Power Engineering 3',
                 'Real Time Computer Systems 3', 'Simulation of Engineering Systems 3', 'Team Design Project EE3',
                 'Advanced Programming and Software Engineering 3']


def grades_html():
    tables = []
    for caption, rows in GRADES:
        body = '\n'.join(f'          <tr><td>{m}</td><td class="cr">{c}</td><td class="gr">{g}</td></tr>' for m, c, g in rows)
        tables.append(f'''      <table class="grade-table">
        <caption>{caption}</caption>
        <thead><tr><th scope="col">Module</th><th scope="col">Credits</th><th scope="col">Grade</th></tr></thead>
        <tbody>
{body}
        </tbody>
      </table>''')
    year3 = ', '.join(YEAR3_MODULES[:-1]) + ' and ' + YEAR3_MODULES[-1]
    return f'''    <div class="grades">
      <h3>Module grades</h3>
      <p class="muted">Glasgow grades run from A1, the highest, down through A5, then B1 to B3, C1 to C3 and so on. A1 to A5 are A grades, the band for first-class work.</p>
      <div class="grade-years">
{chr(10).join(tables)}
      </div>
      <p class="muted">The second semester of Year 2 was the exchange in Chengdu.</p>
      <p><span class="grade-label">Year 3, 2026 to 2027, in progress:</span> {year3}.</p>
    </div>'''


BOM = [
    ('KiCad','Six-layer flight controller with blind vias; two-layer drone kit; ERC, DRC, Gerbers and assembly files'),
    ('OrCAD Capture and Allegro', 'Year 1 boards, designed, built and tested; Year 2 design labs'),
    ('Verilog and Vivado', 'RISC16 processor: datapath, control FSM and testbenches'),
    ('VHDL and Quartus', 'Logic on a MAX 10 FPGA'),
    ('C and C++ on Arm Cortex-M', 'STM32 with Mbed OS; NXP KL25Z at register level'),
    ('SPI, I2C, UART, PWM, interrupts', 'Sensor drivers, motor control and debug output'),
    ('Python', 'Signal processing with NumPy, a build-and-flash tool, Boolean minimisation'),
    ('MATLAB and Simulink', 'Simulation coursework and MathWorks Onramp certificates'),
    ('LTspice, PSpice and Sentaurus TCAD', 'Amplifier and filter labs; p-n junction simulation'),
    ('ABB MOD 300, MOD 300 Advant and 800xA DCS', 'Control logic in Taylor Control Language and card replacement at Sellafield'),
    ('ROS 2 and Boston Dynamics Spot', 'Inspection routes and reference-frame debugging at Sellafield'),
    ('Bench equipment', 'Oscilloscopes, signal generators, bench supplies, soldering and rework'),
]


def index_page():
    parts = '\n'.join(part_html(*f) for f in FEATURED)
    more = '\n'.join(
        f'''<li><div class="row"><span class="ref">{r}</span><h3><a href="{u}">{t}</a></h3><p>{d}</p><a class="go" href="{u}">{"Read more" if u.startswith("projects/") else "View on GitHub"}</a></div></li>'''
        for r, t, u, d in MORE)
    exp = []
    for role, org, when, intro, bullets in EXPERIENCE:
        intro_html = f'<p>{intro}</p>' if intro else ''
        lis = '\n'.join(f'<li>{b}</li>' for b in bullets)
        exp.append(f'''<li>
  <div class="role-head"><h3>{role}</h3><span class="when">{when}</span></div>
  <p class="org">{org}</p>
  {intro_html}
  <ul>
{lis}
  </ul>
</li>''')
    bom = '\n'.join(f'<tr><td>{i + 1}</td><td>{a}</td><td>{b}</td></tr>' for i, (a, b) in enumerate(BOM))
    desc = ('Kartike Sharan, a third-year Electronic and Electrical Engineering student at the University of Glasgow: '
            'PCB design, embedded firmware and digital hardware.')
    return head('Kartike Sharan: electronics, embedded systems and digital design', desc, '', '') + f'''<main id="main">
<div class="board" id="projects">
  <span class="hole tl" aria-hidden="true"></span><span class="hole tr" aria-hidden="true"></span>
  <span class="hole bl" aria-hidden="true"></span><span class="hole br" aria-hidden="true"></span>
  <span class="fid a" aria-hidden="true"></span><span class="fid b" aria-hidden="true"></span>
  <svg class="traces" aria-hidden="true"></svg>
  <header class="titleblock">
    <div>
      <h1>Kartike Sharan</h1>
      <p class="intro">Third-year Electronic and Electrical Engineering student at the University of Glasgow. I lay out circuit boards, write firmware for Arm microcontrollers and build digital logic in Verilog.</p>
      <p class="intro">Looking for a summer 2027 internship in hardware design, verification, embedded systems or electronics.</p>
      {connector()}
    </div>
    <div class="status" aria-hidden="true">
      <span class="led"><i></i>PWR</span>
      <span>Glasgow, Scotland</span>
      <span>{REV}</span>
    </div>
  </header>
  <h2 class="label" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Projects</h2>
  <div class="parts">
{parts}
  </div>
</div>

<section class="section" id="more" aria-labelledby="more-h">
  <div class="wrap">
    <h2 id="more-h">More projects</h2>
    <p class="lede">Smaller pieces of coursework, labs and earlier designs.</p>
    <ul class="rows">
{more}
    </ul>
  </div>
</section>

<section class="section" id="experience" aria-labelledby="exp-h">
  <div class="wrap">
    <h2 id="exp-h">Experience</h2>
    <p class="lede">Most recent first.</p>
    <ol class="timeline">
{chr(10).join(exp)}
    </ol>
  </div>
</section>

<section class="section" id="skills" aria-labelledby="skills-h">
  <div class="wrap">
    <h2 id="skills-h">Skills</h2>
    <p class="lede">Laid out like a bill of materials, with where I've used each one.</p>
    <table class="bom">
      <thead><tr><th scope="col">Item</th><th scope="col">Part</th><th scope="col">Where I've used it</th></tr></thead>
      <tbody>
{bom}
      </tbody>
    </table>
  </div>
</section>

<section class="section" id="education" aria-labelledby="edu-h">
  <div class="wrap">
    <h2 id="edu-h" style="margin-bottom:28px">Education and awards</h2>
    <div class="edu">
      <div>
        <h3>University of Glasgow</h3>
        <p>BEng (Hons) Electronics and Electrical Engineering, 2024 to 2028</p>
        <p class="muted">Third year. Expected First Class Honours; current average 20/22 (A band).</p>
      </div>
      <div>
        <h3>UESTC, Chengdu</h3>
        <p>Year 2 exchange semester, Feb to Jul 2026</p>
        <p class="muted">Funded by a China Link Scholarship. Embedded Processors: 82%.</p>
      </div>
      <div>
        <h3>Belmont House School</h3>
        <p>Advanced Highers: Mathematics (A), Physics (B)</p>
        <p class="muted">Six Highers at A to B.</p>
      </div>
      <div>
        <h3>Awards</h3>
        <p>Engineering Excellence List (2025); China Link Scholarship (2026); Passant Cup for Mathematics (2024); UKMT Best in School for Mathematics (2023); represented Scotland at chess (2020).</p>
      </div>
      <div>
        <h3>Languages</h3>
        <p>English (native); Hindi, Nepali and Urdu (fluent spoken); Punjabi (conversational).</p>
      </div>
    </div>
{grades_html()}
  </div>
</section>
</main>
''' + footer('')


def not_found():
    return head('Page not found: Kartike Sharan', 'This page does not exist.', '/', '404.html') + '''<main id="main" class="wrap" style="padding-top:12vh">
  <p class="ref" style="color:var(--accent-text)">Open circuit</p>
  <h1 style="font-size:var(--step-3);margin:10px 0 16px">There's no page at this address</h1>
  <p class="prose">The link may be out of date. Everything on the site starts from the <a href="/">home page</a>.</p>
</main>
''' + footer('/')


def sitemap():
    urls = [f'{SITE}/'] + [f'{SITE}/projects/{p["slug"]}.html' for p in PROJECTS]
    body = '\n'.join(f'  <url><loc>{u}</loc></url>' for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'projects'), exist_ok=True)
    open(os.path.join(ROOT, 'index.html'), 'w').write(index_page())
    for i, p in enumerate(PROJECTS):
        open(os.path.join(ROOT, 'projects', p['slug'] + '.html'), 'w').write(project_page(i, p))
    open(os.path.join(ROOT, '404.html'), 'w').write(not_found())
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sitemap())
    print('built', 2 + len(PROJECTS), 'pages')
