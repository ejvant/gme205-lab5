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

## OOAD Notes

- *Analysis:* The problem asks for a parcel to be checked against several independent 
  development rules. The domains are parcel, hazard zone, rule, result, and assessment. 
  The part most likely to change is the set of rules.
- *Design:* Each rule object decides one criterion. `ParcelAssessment` coordinates all rules on every `AssessmentRule`. `Parcel` and `HazardZone` own their own state and spatial behavior. `RuleResult` carries each rule's answer. 
- *Implementation:* `ABC` + `@abstractmethod` for the rule contract, subclasses for each rule, a frozen dataclass for `RuleResult`, read-only properties for encapsulation and composition, and a thin runner that only builds and runs the objects.

## UML Class Diagram

The UML class diagram is stored at: `diagrams/lab 5 uml.png`

## The Four Pillars in the Converted Code

| Pillar | UML Evidence | Code Evidence | Why It Matters |
|---|---|---|---|
| Encapsulation | Parcel owns zone and area_sqm | `Parcel.__init__` validates the ID, geometry, zone, and area; read-only properties are used to access values | Ensures that a parcel cannot be created with an invalid state. |
| Abstraction | «abstract» `AssessmentRule` | `class AssessmentRule(ABC)` with `@abstractmethod evaluate` | Defines what every rule must do without specifying how it is implemented. |
| Inheritance | Rule classes point to `AssessmentRule` | `class MinimumAreaRule(AssessmentRule)` with `super().__init__(...)` | Provides a shared contract and avoids repeating common rule information. |
| Polymorphism | All rule classes expose `evaluate(parcel)` | `rule.evaluate(self._parcel)` in `ParcelAssessment.evaluate()` | Coordinator works with the interface, not concrete rule types. |

## Extension Without Coordinator Rewrite

For the extension, I added a `Road` class and a `RoadAccessRule` that inherits `AssessmentRule`. The rule stores one `Road` and a `max_distance`, and passes when `parcel.geometry.distance(road.geometry) <= max_distance`.
I placed RD-01 along y = -10 and used a 20 m threshold, so both parcels are 10 m from the road.

**Original rules list**
```python
rules = [
    MinimumAreaRule(5000),
    AllowedZoneRule({"Residential", "Commercial"}),
    NoHazardOverlapRule(hazard),
]
```

**New rules list**
```python
rules = [
    MinimumAreaRule(5000),
    AllowedZoneRule({"Residential", "Commercial"}),
    NoHazardOverlapRule(hazard),
    RoadAccessRule(road, 20),
]
```

**Unchanged `ParcelAssessment.evaluate()`**
```python
def evaluate(self):
    results = []
    for rule in self._rules:
        result = rule.evaluate(self._parcel)
        results.append(result)
    return results
```

**Why this is different from adding an `elif` branch**

A weak design would make the coordinator check the rule type:

```python
if rule_type == "minimum_area":
    ...
elif rule_type == "allowed_zone":
    ...
elif rule_type == "hazard_overlap":
    ...
elif rule_type == "road_access":
    ...  
```

With that design, `ParcelAssessment` has to know every rule type again and again. So, each new rule means reopening and re-testing the coordinator, and the rule's logic ends up living in the coordinator instead of in the rule. The new design `ParcelAssessment` depends only on the `AssessmentRule` contract, so adding `RoadAccessRule` only required adding one object to the rules list. Thus, `evaluate()` was not changed.

## Reflection

1. *OOAD:* Creating a model for the problem changed how I approached the whole implementation because it helped me distinguish which responsibilities should belong to each class. So, instead of putting all the development criteria inside `Parcel`, I realized that these rules should be handled by separate rule objects. This allows `Parcel` to focus only on its own properties and spatial behavior, while the rule classes handle the assessment logic. 

2. *Candidate classes:* I chose not to create a separate class for "zoning classification" because it is just a string value stored in `Parcel` and has no identity nor behavior of its own. The decision about which zones are allowed is handled by `AllowedZoneRule`. 
 
3. *Encapsulation:* The `Parcel` stores its ID, geometry, zone, and area as its attributes and provides read-only properties for accessing them. This allows for retrieving values such as `parcel.area_sqm` in other parts of the program without directly modifying them. The constructor also rejects a missing ID, missing geometry, blank zone, and an area that is zero or negative. This helps keep the parcel data valid and reliable for the assessment rules. 

4. *Abstraction:* The `AssessmentRule` promises that every rule has a name and an `evaluate(parcel)` method that produces a `RuleResult`. It does not include specific details of how each rule works. These details are handled by the individual subclasses. Since `evaluate` is abstract, `AssessmentRule` serves only as a blueprint and cannot be instantiated.

5. *Inheritance:* All concrete rule classes inherit the common features of `AssessmentRule`, including the constructor that stores the rule name using `super().__init__(...)`, the read-only `name` property, and the required `evaluate(parcel) -> RuleResult` method. Each subclass then adds its own specific configuration, such as `min_area`, `allowed_zones`, `hazard_zone`, or `road`, along with its own implementation of the `evaluate` method.

6. *Polymorphism:* Each object stored in `ParcelAssessment._rules` follows the `AssessmentRule` interface and therefore provides an `evaluate(parcel)` method. The assessment loop calls the same method for every rule. On the other hand, Python uses the implementation defined by the specific rule object. This allows `ParcelAssessment` to work with different rule types without needing separate `if/elif` statements to identify them.

7. *Composition:* `ParcelAssessment` is neither a parcel nor an assessment rule. Instead, it works with one parcel and a collection of rules. Using inheritance would give the assessment unnecessary attributes and behaviors that do not belong to it. 

8. *Extension:* I extended the system by adding a `Road` class with an ID and `LineString` geometry, along with a `RoadAccessRule` subclass that checks whether a parcel is within the specified maximum distance from a road. A new rule is added to the rule list, and additonal tests were created. No changes were needed in `ParcelAssessment` or the existing rules. 

10. *UML-to-Code Consistency:* When I compared the final UML diagram with the actual implementation, I noticed two differences: `AllowedZoneRule` was shown using a `frozenset` in the diagram, while the code used a `set`, and `ParcelAssessment.to_dict()` was not included in the UML even though it is used by the runner. I corrected the diagram to match the final code. 

## Author
Enoch Joshua V. Antonio  
MS Geomatics Engineering

## References

- Python `abc` module – Abstract Base Classes: <https://docs.python.org/3/library/abc.html>
- Python `dataclasses`: <https://docs.python.org/3/library/dataclasses.html>
- Python Classes Tutorial: <https://docs.python.org/3/tutorial/classes.html>
- Shapely – Geometry and Predicates: <https://shapely.readthedocs.io/>
- pytest Documentation: <https://docs.pytest.org/>
- diagrams.net / draw.io: <https://www.diagrams.net/>

Edited on GitHub web interface and VS Code