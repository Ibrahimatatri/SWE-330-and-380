# SWE-330-and-380
Joint project repository for the presentation of both classes. We have opted, with approval, to construct a single compiled project that should fulfill the presentation requirements of both assignments.

# Background
We have access to public datasets involving many language-model Skills files and an extent of related information about them 
The quick example was that a slight majority, 50.5%, are copied across projects without editing.

We should have access to a large scale of visible repositories and the application of the skills, should we want to analyze their specific use

The mining challenge places emphasis on "exploring novel research questions and presenting insights", which means we can ask any tangentially related question and work from there.

# First Phase Requirements & Notes
- We must identify a question, ideally that we each find interesting, related to and investigable by one of the MSR datasets.
- We learn toward the GitSkills dataset so far.

- We must identify, flesh out, and prepare for a 'software problem' derived from the question we pose. 
  - We must present our intended learning objective(s) in working on that problem, so beginning with an interesting query is somewhat important.
  - The problem must be defined by a party who experiences it, why it is currently difficult to solve, and what we plan to investigate for an answer. This does not mean that we find an answer, it will not be uncommon or detrimental to perform sufficient analysis without concrete results.

- We must lay out the scope of our problem -- obvious related concepts that fall within or outside of the scope of our analysis. This is necessary to know what not to waste time on.
This scope analysis will include our set of assumptions (about the dataset, users related to the problem, available technology, etc.)
  - We must identify the stakeholders of the system we intend to analyze. 
  - For each major class of stakeholder, we must identify their likely goals, concerns, and expectations.

- We must state the primary goal of the problem analysis in the GQM format given: "Analyze [subject] with the intent of [purpose], with respect to [quality concerns], from the perspective of [stakeholder], in the context of [environment]."

# Our chosen direction
Our agreed idea will be to scan an amount of provided skills markdown files for:
A. Names of common-use AI models or indication that the skill is aimed at a particular model
B. Included executable, batch, shell, etc. files or instructions to use them

This would provide information as to whether skills are often targeted at particular models, and a potential indication as to the level of trust afforded to those models over others
