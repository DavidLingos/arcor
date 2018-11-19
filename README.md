# ARCOR (formerly known as ARTable) - the main repository

[![Build Status](https://travis-ci.org/robofit/arcor.svg)](https://travis-ci.org/robofit/arcor)

ARCOR - vision of a near future workspace, where human and robot may safely and effectively collaborate. Our main focus is on human-robot interaction and especially on robot programming - to make it feasible for any ordinary skilled worker. The interaction is based mainly on interactive spatial augmented reality - combination of projection and touch sensitive surface. However, more modalities are integrated or currently under development.

### Repositories / packages

This repository holds the main components of the system, which are not specific to any particular setup (combination and type of components) or robot:

 * [art_brain](https://github.com/robofit/arcor/tree/master/art_brain) - central node which communicates with robot, manages program execution, holds current system state etc.
 * [art_bringup](https://github.com/robofit/arcor/tree/master/art_bringup) - to launch the system.
 * [art_calibration](https://github.com/robofit/arcor/tree/master/art_calibration) - AR marker-based mutual calibration of cameras.
 * [art_collision_env](https://github.com/robofit/arcor/tree/master/art_collision_env) - manages detected as well as artificial objects within the workspace.
 * [art_db](https://github.com/robofit/arcor/tree/master/art_db) - permanent storage for object types, programs, etc.
 * [art_instructions](https://github.com/robofit/arcor/tree/master/art_instructions) - for each supported instruction there is its definition in yaml and respective classes for art_brain and art_projected_gui. Those classes are loaded on startup based on ```/art/instructions``` parameter.
 * [art_led](https://github.com/robofit/arcor/tree/master/art_led) - RGB LED strip interface.
 * [art_projected_gui](https://github.com/robofit/arcor/tree/master/art_projected_gui) - shows system state, allows to set program parameters, etc. 
 * [art_projector](https://github.com/robofit/arcor/tree/master/art_projector) - calibrates projector wrt. Kinect and displays scene generated by art_projected_gui. 
 * [art_simple_tracker](https://github.com/robofit/arcor/tree/master/art_simple_tracker) - not a real tracker, it "tracks" objects based on already assigned IDs and performs position/orientation filtering from multiple detectors.
 * [art_sound](https://github.com/robofit/arcor/tree/master/art_sound) - a sound interface: plays sound for selected system events (error).
 * [art_table_pointing](https://github.com/robofit/arcor/tree/master/art_table_pointing) - uses Kinect skeleton tracking to compute where user points on the table.
 * [art_touch_driver](https://github.com/robofit/arcor/tree/master/art_touch_driver) - reads data from touch foil (which is HID device) a publishes it as ROS messages.

Additional repositories:

 * [arcor-msgs](https://github.com/robofit/arcor-msgs) [![Build Status](https://travis-ci.org/robofit/arcor-msgs.svg?branch=master)](https://travis-ci.org/robofit/arcor-msgs) - ROS messages, services, actions.
 * [arcor-utils](https://github.com/robofit/arcor-utils) [![Build Status](https://travis-ci.org/robofit/arcor-utils.svg?branch=master)](https://travis-ci.org/robofit/arcor-utils) - Python helper classes.
 * [arcor-detectors](https://github.com/robofit/arcor-detectors) [![Build Status](https://travis-ci.org/robofit/arcor-detectors.svg?branch=master)](https://travis-ci.org/robofit/arcor-detectors) - detectors (currently, only AR code detector wrapper).

For each integrated robot, there are two repositories: one with custom packages providing high-level functions compatible with arcor ROS API and one with implementation of art_brain plugin (```-interface``` one):

* PR2
  * [https://github.com/robofit/arcor-pr2](https://github.com/robofit/arcor-pr2) [![Build Status](https://travis-ci.org/robofit/arcor-pr2.svg?branch=master)](https://travis-ci.org/robofit/arcor-pr2)
  * [https://github.com/robofit/arcor-pr2-interface](https://github.com/robofit/arcor-pr2-interface) [![Build Status](https://travis-ci.org/robofit/arcor-pr2-interface.svg?branch=master)](https://travis-ci.org/robofit/arcor-pr2-interface)
* DOBOT Magician
  * [https://github.com/robofit/arcor-dobot](https://github.com/robofit/arcor-dobot) [![Build Status](https://travis-ci.org/robofit/arcor-dobot.svg?branch=master)](https://travis-ci.org/robofit/arcor-dobot)
  * [https://github.com/robofit/arcor-dobot-interface](https://github.com/robofit/arcor-dobot-interface) [![Build Status](https://travis-ci.org/robofit/arcor-dobot-interface.svg?branch=master)](https://travis-ci.org/robofit/arcor-dobot-interface)
* Empty (dummy) arm
  * [https://github.com/robofit/arcor-empty-arm](https://github.com/robofit/arcor-empty-arm) [![Build Status](https://travis-ci.org/robofit/arcor-empty-arm.svg?branch=master)](https://travis-ci.org/robofit/arcor-empty-arm)

Currently supported setups (see links for further information):

 * [arcor setup 1](https://github.com/robofit/arcor-setup-1) [![Build Status](https://travis-ci.org/robofit/arcor-setup-1.svg?branch=master)](https://travis-ci.org/robofit/arcor-setup-1)
 * [arcor setup 2](https://github.com/robofit/arcor-setup-2) [![Build Status](https://travis-ci.org/robofit/arcor-setup-2.svg?branch=master)](https://travis-ci.org/robofit/arcor-setup-2)
 * [arcor setup 3](https://github.com/robofit/arcor-setup-3) [![Build Status](https://travis-ci.org/robofit/arcor-setup-3.svg?branch=master)](https://travis-ci.org/robofit/arcor-setup-3)
 
 Any supported setup may be used with any supported robot (or even without one).

### Functionality

The system has two main modes: setting program parameters and program execution.

The video below briefly introduces the system and shows how we did its first UX testing:

[![arcor video](https://i.ytimg.com/vi/cQqNLy6mE8w/0.jpg)](https://www.youtube.com/watch?v=cQqNLy6mE8w)

Currently, the robot program has to be created beforehand (e.g. using script like [this](https://github.com/robofit/arcor/blob/master/art_db/scripts/simple_trolley.py). Then, program parameters could be easily set using the projected interface. In order to make setting parameters as simple as possible, the system is based on complex instructions, with high-level of abstraction (for supported instructions see [instructions.yaml](https://github.com/robofit/arcor/blob/master/art_instructions/config/instructions.yaml)).

### API

All topics, parameters and services can be found in `/art` namespace.

TBD

### Installation

TBD

### Contributing

 - Follow [PyStyleGuide](http://wiki.ros.org/PyStyleGuide) or [CppStyleGuide](http://wiki.ros.org/CppStyleGuide)
   - for Python, you may use [pre-commit hook](https://github.com/robofit/arcor/blob/master/hooks/pre-commit) to automatically format your code according to PEP8 (just copy the file into .git/hooks).
 - Use [catkin_lint](http://fkie.github.io/catkin_lint/) to check for common problems (```catkin_lint -W2 your_package_name```)
 - Use [roslint](http://wiki.ros.org/roslint) to run static analysis of your code.
 - Ideally, create and use unit tests.
 - Feel free to open pull requests!

### Publications

 * MATERNA Zdeněk, KAPINUS Michal, BERAN Vítězslav, SMRŽ Pavel a ZEMČÍK Pavel. Interactive Spatial Augmented Reality in Collaborative Robot Programming: User Experience Evaluation. In: Robot and Human Interactive Communication (RO-MAN). NanJing: Institute of Electrical and Electronics Engineers, 2018 (to be published).
 * MATERNA Zdeněk, KAPINUS Michal, BERAN Vítězslav a SMRŽ Pavel. Using Persona, Scenario, and Use Case to Develop a Human-Robot Augmented Reality Collaborative Workspace. In: HRI 2017. Vídeň: Association for Computing Machinery, 2017, s. 1-2. ISBN 978-1-4503-4885-0.
 * MATERNA Zdeněk, KAPINUS Michal, ŠPANĚL Michal, BERAN Vítězslav a SMRŽ Pavel. Simplified Industrial Robot Programming: Effects of Errors on Multimodal Interaction in WoZ experiment. In: Robot and Human Interactive Communication (RO-MAN). New York City: Institute of Electrical and Electronics Engineers, 2016, s. 1-6. ISBN 978-1-5090-3929-6.
