# GmE 205: Laboratory Exercise 5
**Object-Oriented Spatial Modeling with UML**
## Overview
*The laboratory exercise focuses on identifying spatial objects, assigning responsibilities, and representing their relationships through UML before implementing the design in Python. The system applies the four pillars of OOP (encapsulation, abstraction, inheritance, and polymorphism), together with composition and spatial operations using Shapely. The UML model is then forward-engineered into modular Python classes, tested using pytest, and documented through JSON output, README reflection, UML diagrams, and Git/GitHub version history.*

## How to set up the virtual environment
The steps to set up a virtual environment:
1. Open Visual Studio Code.
2. Under the VS Code Terminal tab, select "New Terminal".
3. In the Terminal, run:

   `py -m venv .venv`

   `.\.venv\Scripts\activate`

4. When successful, your terminal prompt should show `(.venv)`.

## Problem Statement

A local planning team intends to use a simple program that screens land parcels against a set of independent development rules. Each parcel has an ID, geometry, zoning classification, and a recorded area in square meters. The initial system (Version 1) applies three (3) rules: the minimum area requirement, an allowable zoning classification, and a hazard rule that indicates parcels must not touch a mapped hazard zone. 

Each rule must return a result that includes the rule name, pass/fail, and a short reason. An assessment combines all rules into one report with an overall decision. The system should also be designed for extensibility, which allows to add a new rule (e.g. road access) without rewriting the code/assessment loop. 

## Candidate-class Table

## Candidate-Class Table

| Phrase from Problem | Initial Interpretation | Keep as Class? | Reason |
|---|---|---|---|
| planning team | actor/stakeholder | No | The team uses the system; it has no state or behavior. |
| parcel | domain entity | Yes | It has its own identity, state, geometry, and spatial behavior. |
| identifier, geometry | parcel state | No | These are plain values carried by a spatial object and have no behavior of their own. |
| zoning classification | parcel state | No | A string value carried by `Parcel`. |
| area in square meters | parcel state | No | A numeric value carried by `Parcel`. The threshold is handled by `MinimumAreaRule`. |
| hazard zone | domain entity | Yes | It has its own identity, geometry, hazard type, and severity. It is referenced by a rule, so it is modeled as a separate object rather than a parcel attribute. |
| assessment rule | behavioral abstraction | Yes | Every rule answers the same question and follows a common contract shared by all rule variants. |
| minimum area / allowed zones / hazard overlap | specialized rules | Yes (3 subclasses) | Each rule has its own configuration and decision logic: threshold, allowed zones, or hazard object. |
| result (name, pass/fail, explanation) | value object | Yes | Provides a consistent result structure for all rules. |
| parcel assessment | coordinator | Yes | Runs every rule on a parcel and combines their results into one assessment. |
| report | output representation | Not yet | A JSON-ready dictionary is sufficient; a `Report` class would add little responsibility. |
| road (extension) | domain entity | Yes | Like a hazard zone, it has its own identity and geometry and can be referenced by `RoadAccessRule`. |

