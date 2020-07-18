

# Fuzzer Design Document

Andrew Kaploun, Frances Lee, Aran Pando, Michael Theos


### Guide to reading the document:

We will often give a top-level overview, then explain key terms afterwards. Items in **bold** indicate they do not need to be fully understood, as we will explain them in more detail in the relevant section of the document.


## Execution Flow:

The main execution flow of our program can be described as below:


```
while true:
	input <- queue.get()
resultStats <- runInput(input)
if resultStats.isCrash():
	break_and_record_failure()
	cache[input] = resultStats
	for tactic in tactics:
		for mutation in $TYPE_mutator(tactic):
    	queue.put([mutation, resultStats])
```


Looking at our current code for the tactics and mutators, it is clear they can be heavily inlined. However, we intend to heavily extend these functions and classes, so this abstraction is worth it. 


# Class Explanation and Plans:


## Mutator Tactics:

We will take some inspiration from AFL ([https://lcamtuf.blogspot.com/2014/08/binary-fuzzing-strategies-what-works.html](https://lcamtuf.blogspot.com/2014/08/binary-fuzzing-strategies-what-works.html)) in that we explicitly name a number of different ‘tactics’ for mutating the input.

Our approach differs from AFL in that we make customizations that account for the fact that we know the structure of the program. Whilst AFL does inputs in the following order:



*   A bunch of special cases like INT_MAX
*   Bitflips on the original seed input
*   Finally, splicing together various cases to incorporate the seed input with INT_MAX somewhere

However, for our approach: since we know the structure of the data, we can mutate our fields with special values as one of our tactics, and prioritise this mutation heavily.

We will engage in many ways (tactics) for generating a list of inputs given one input:



*   Bitflip tactic (planned to be implemented in final program): 
    *   For each bit:
        *   Generate a mutation with that bit flipped
*   Miscellaneous tactic: Generate an input that adds a level of nesting in the JSON/XML list or dictionary, an input that deletes a character, an input that deletes a character, an input that increments a character, and so on
*   ‘Meme’ tactic:
    *   Generates inputs with things like format strings, int_max, 0, -1, that are ‘brute force’ special cases. 

Currently, we use the ‘meme’ tactic and the miscellaneous tactic, since bitflips are small changes and won’t work as well without a code coverage metric.


#### Implementation detail (TYPE_mutator):

At the beginning of our program, we detect the type of the input and, correspondingly, decide to use one of the file type mutators.We use the mutators to implement the bigflip tactics. 



*   JSON mutator
*   CSV mutator
*   XML mutator
*   text file mutator

These mutators call the individual type mutators for all the primitive types in JSON:



*   int
*   string
*   float
*   boolean
*   JSON object (dictionary)
*   list


## Result Stats (and **measure**):

When we run the program, we put in an input, and receive some outputs like the 



*   Result code (segfault, etc.)
*   Tactic used to get to this 
*   **Distance **from the original input

The distance is just the number of times we have mutated the input from the initial input. example. if we mutate a string a -> b -> c -> d, the “distance” of a is 0 and the “distance” of d is 3. 


## Result Stats Plan:

We intend to extend this use the 

*   Input length 
*   **Code coverage**

One wonders at this point why we use a priority queue. Reasoning: For the priority, let’s say the sample CSV input is “5, strin” and then consider the following CSVs:



*   0
*   -1
*   5, strin
*   4, strin

We would first like to test the given sample case and then the zero edge case, however, we would like to prioritise mutations on the sample test case instead of the zero edge case, since we could get a buffer overflow on “4, strin”. 

Thus, we create a measure that is a function of all of the above results, which assigns lower values (higher priority) to inputs that increase code coverage, inputs with lower input length, inputs with lower distance from the original input, and other favourable properties. 


## Coverage:

Code coverage will be the main heuristic that we use to separate an ‘unsuccessful’ case from a successful case, and the main weighting factor for our priority queue. 


### Coverage Plan: 


#### (GDB/MI):

GDB/MI is an execution mode of GDB that gives a structured output for computers to read, instead of human-readable output.

We would use this to track execution cycles by setting breakpoints at every jump, and thus at every breakpoint, reading whether we jump or not, and thus knowing the code path. 

This would be very expensive, since even if we don’t jump, we still perform a bunch of I/O since we hit a GDB breakpoint.


#### qemu:

We will either use GDB/MI or qemu. qemu has a large startup time. AFL does a lot of scary and complicated things to modify qemu to make it faster, so we will need to figure out which optimisations we can omit.
