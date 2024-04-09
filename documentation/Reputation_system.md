# Reputation System Documentation

## Introduction
The reputation system within the automoderation functionality serves to assess the trustworthiness of users based on their behavior and interactions within the system. This documentation outlines the implementation and functionality of the reputation system.

## Trustworthyness Determination
The reputation of someone can range from -10 to +10.<br>
There are multiple tracked reputations for a user:
- Usage of slurs
- Usage of swears<br>

The reputation of each item is determined by the following factors:
- The number of times the user has tripped a check looking for that item

## Reputation System Implementation
The reputation system is put into action by the files in ./cogs/automod/passive/<br>
The files antislur and antiswear both call upon the function automod.repHeuristic. <br>
This function is located in ./cogs/automod/automod.py<br>

## Difflib.SequenceMatcher usage in Similarity check
The function automod.repHeuristic uses the SequenceMatcher from the difflib library to check the similarity between the slur/swear and the message. <br>
We convert their usual 0.0-1.0 similarity ratio to a 0-100 ratio for users to be able to have a better conceptual understanding of the data.

### Reputation Calculation
The reputation of a user is calculated by the following code
```python
rep_value = 0 # Default reputation for a new user
sim_ratio = 85 # Starting similarity ratio
for i in range(int(rep_value), 11):
    if rep_value < 0:
        # If the reputation is negative, the similarity ratio is increased
        sim_ratio -= 3.5
    else:
        sim_ratio -= 3
```

## Storage
If using json files, the reputation of a user is stored in a json file in ./memory/users/<uuid>/reputation.json<br>
Otherwise, it'll be stored in the DB in the table 'users'<br>
It is always stored as a float.

<hr>

# Summary
The reputation system is a system that tracks the trustworthiness of a user based on their behavior. The reputation of a user is determined by the number of times they have tripped a check for slurs or swears.