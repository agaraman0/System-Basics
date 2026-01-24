Given an integer array nums, design an algorithm to randomly shuffle the array. All permutations of the array should be equally likely as a result of the shuffling.

Implement the Solution class:

Solution(int[] nums) Initializes the object with the integer array nums.
int[] reset() Resets the array to its original configuration and returns it.
int[] shuffle() Returns a random shuffling of the array.


arr = [2,4,6,9,10,13,6]

reset() -> arr[]
shuffle() - [4,9,10,13,6,6,2]

[10,13,6,2,4,6,9]


xxxx73%7 - 3

random(5) -> [0,5)

shuffle_arr[n]

for i in range(n):
  flag = False
  while Flag:
    r_i = random(n)
    if shuffle_arr[r_i] == inf:
      shuffle_arr[r_i] = arr[i]
      flag = True

class Solution():

  def __init__(self, arr):
    self.arr = arr
    self.length = len(arr)

  def reset(self):
    return self.arr

  def shuffle(self):
    shuffle_arr = [10**6] * self.length
    for i in range(self.length):
      flag = False
      while Flag: //infinite
        r_i = random(self.length)
        if shuffle_arr[r_i] == inf:
          shuffle_arr[r_i] = arr[i]
          flag = True
    return shuffle_arr

T: 
S: 

Approach with examples, time/space complexity, code (10 min), dry run (5 min), optimizations/cross questions

Initial Communication is required when trying to understand the problem
explain approach clearly


Brainstorming: try it on the shared screen, untill or unless you need to draw something. 
Keep it vocal

Interveiwer didn't know what you were thinking

class structure is good, picked that up quickly











  


