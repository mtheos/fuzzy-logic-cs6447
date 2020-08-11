



# Fuzzer Design Document

Andrew Kaploun, Frances Lee, Aran Pando, Michael Theos




![beautiful](https://i.imgur.com/mgv0XQo.png "image_tooltip")





#### Guide to reading the document

We will often give a top-level overview, then explain key terms afterwards. Items in **bold** indicate they do not need to be fully understood, as we will explain them in more detail in the relevant section of the document. 


## Execution Flow

The execution flow of our program is shown below, extended from our midpoint submission:


```
while true:
    while hasInputs() and not tooManyRunning():
        input <- getInput()
        async queueRun(input)
    while existsCompletedRuns():
        resultStats <- getResult()
        if resultStats.isCrash():
            finish_and_record_success()
        cache[input] = resultStats
        mutateEventually(resultStats)
    while existsInputsToMutate()and not tooManyQueued():
        prevResult <- getMutate()
        for tactic in tactics:
            for mutation in $TYPE_mutator(prevResult, tactic):
                newInput(mutation)
```


The new paradigm can be split into 3 stages; running, checking, mutating. First, we queue available inputs up to a limit, then we retrieve the results of these runs and 

a) check if we're done, 

b) queue inputs to be mutated,

c) we mutate to produce new inputs which can use many strategies.


# Design


## Mutator Tactics

We take some inspiration from AFL ([https://lcamtuf.blogspot.com/2014/08/binary-fuzzing-strategies-what-works.html](https://lcamtuf.blogspot.com/2014/08/binary-fuzzing-strategies-what-works.html)) in that we explicitly name a number of different ‘tactics’ for mutating the input.

Our approach differs from AFL in that we make customizations that account for the fact that we know the structure of the program. Whilst AFL does inputs in the following order:



*   A bunch of special cases like INT_MAX
*   Bitflips on the original seed input
*   Finally, splicing together various cases to incorporate the seed input with INT_MAX somewhere

However, for our approach: since we know the structure of the data, we can mutate our fields with special values as one of our tactics, and prioritise this mutation heavily.

We engage in many ways (tactics) for generating a list of inputs given one input:



*   Bitflip tactic: 
    *   For each bit:
        *   Generate a mutation with that bit flipped
*   Miscellaneous tactic: 
    *   Generate an input that adds a level of nesting in the JSON/XML list or dictionary,
    *   an input that deletes a character, 
    *   an input that inserts a character, 
    *   an input that adds/subtracts an integer/float,
    *   and so on
*   ‘Meme’ tactic:
    *   Generates inputs with things like format strings, int_max, 0, -1, long strings; that are ‘brute force’ special cases.

Currently, we use the ‘meme’ tactic and the miscellaneous tactic, since bitflips are small changes and won’t work as well without a code coverage metric.

Since the midpoint check-in we have added **code coverage** to the program. The same tactics are used to generate randomly mutated inputs, however, the code coverage guides input mutation in the right direction. More information on that in the _Something Awesome_ section.


### Implementation detail (TYPE_mutator)

At the beginning of our program, we detect the type of input and correspondingly decide to use one of the file type mutators. These file mutators mutate the input file.



*   JSON mutator
*   CSV mutator
*   XML mutator
*   Plain text mutator

These mutators call individual type mutators for all the primitive types in JSON:



*   int
*   string
*   float
*   boolean
*   JSON object (dictionary)
*   List


#### Native-Type (TYPE_mutator) Mutation Strategies



1. Insert min and max
2. Make zero (makes numbers zero and makes strings empty)
3. add/subtract by a randomly large number
4. bitflip
    1. clarification: return 1 thing with the first bit flipped, another thing with the second bit flipped, etc…)
5. byteflip (flip a sequence of 8 bytes)
6. Insert %n%s format string
7. Append large string (adam, etc.)
8. put in non-ascii characters into string

*page 1/2*

### Meme mutations



*   We created an “adam” string generator which generates a random large amount of “adam”s. 
*   Nesting a very large amount of elements inside an xml file
*   Creating a very ‘long’ xml file with many elements


## Result Stats (and **measure**)

When we run the program, we pipe in an input and receive some outputs like: 



*   Result code (segfault, etc.)
*   Strategy used to get to this 
*   **Distance **from the original input

The distance is just the number of times we have mutated the input from the initial input. example. if we mutate a string a -> b -> c -> d, the “distance” of a is 0 and the “distance” of d is 3. 


## Important things that affect the measure



*   Whether we are doing ‘small’ strategies or ‘big ad-hoc’ strategies
*   the size of the input
*   coverage


## Queue

Our executor maintains a queue of tasks to run, which is fed from a queue of “ready to run” inputs. Managing the size of these queues is important as a long queue is faster but less flexible. Flexibility is important as the executor will run inputs in the order given and we don’t want to saturate it with inputs only to find that future inputs have a higher priority function (and thus more likely to produce a successful fuzz). To manage this we start with a small queue and after an initial delay (to let things ramp up) we monitor the executor for stall (no jobs), and if it has stalled we increase the maximum number of jobs queued at once as well as the number of jobs ready to go so we can always keep it fed. The optimal length of the queue is inversely proportional to how long a program takes to run.


### Idea behind using a priority queue:

One wonders at this point why we use a priority queue. Reasoning: For the priority, let’s say the sample CSV input is “5, strin” and then consider the following CSVs:



*   0
*   -1
*   5, strin
*   4, strin

We would first like to test the given sample case and then the zero edge case, however, we would like to prioritise mutations on the sample test case instead of the zero edge case, since we could get a buffer overflow on “4, strin”. 

Thus, we create a measure that is a function of all of the above results, which assigns lower values (higher priority) to inputs that increase code coverage, inputs with lower input length, inputs with lower distance from the original input, and other favourable properties. 


## Memory Management

Once we started using QEMU, managing memory became an important part of our design. Compromises had to be made to keep our program from consuming all system resources. The trace files produced by QEMU are big, typically 1 to 15mb, and even once we strip out extra information they are still quite large and over the course of fuzzing (3-minutes) they can consume a significant amount of memory (2 - 3GB). Additionally, our mutator produces a quadratic (n^2) growth of inputs which while not individually large (except for a few meme cases) add up significantly. In order to manage this we did two main things:



1. We maintain a buffer of “ready to go” inputs and don’t fuzz more inputs until that buffer is low, this reduces a quadratic input growth to a linear one.
2. When memory is scarce (&lt; 400 MB) we delete traces for old generations of inputs, because of our priority queue these inputs are excellent candidates to clean up as they will either already have been fuzzed or have a low priority to fuzz


# Something awesome:


## Code Coverage:

Code coverage will be the main heuristic that we use to separate an ‘unsuccessful’ case from a successful case, and the main weighting factor for our **priority queue**. 


### QEMU:

We use the QEMU user-space emulator mode to get a list of blocks that we enter in the code. We haven't implemented the optimisations AFL does to make QEMU work faster, but since AFL has to work with binary data and we have a good starting point from our initial input + known input type + mutation strategies built for the inputs we're fuzzing, we don't typically need the horsepower AFL does to find faults.

What we gather is the transition between every two blocks in the code.

Also, we ignore transitions into and out of libc.

A big part of qemu is integrating it into our program in an effective way. Our overall strategy is to do the following:



*   First do small mutations whilst tracking coverage intently. This is important so that we access all the code paths
*   Later do large mutations where we don’t care as much about their coverage.

We use pwntools to figure out if a binary is 32 bit or 64 bit, and adjust the parsing of the trace based on this.


## Multiprocessing

By far the slowest aspect of fuzzing is running the target binary with an input, and in the case of using QEMU there is an additional penalty to running it natively. As such we implemented a multiprocess executor class that runs our inputs in parallel to maximize hardware utilization. Initially, we assumed that using the same number of processes as cores would be optimal as running the target binaries is likely to be CPU bound (if not in the binary itself then in QEMU). And while this gave the greatest leap in performance, through testing we found that performance continued to improve until we had 2x the number of cores in processes (I believe I/O blocking is the main contributor to this). We initially built this using a thread pool executor but found switching to a process pool executor was more than 3x faster (just GIL things…).


# Improvements to make:

We made a large number of critical mistakes when doing this project.


#### Implementation

We wrote some code that mutated XMLs, CSVs, JSON, plaintext, and planned on applying different mutation ‘strategies’ later. It ended up being really hard to wire the strategies into the code effectively since the code without the strategies was ad-hoc optimized to work as-is. Also, it would have required a lot of refactoring of the existing code.


#### Fault detection

Our fuzzer can also only detect segfault errors, which means there could be overflow, use after free, or general corruption we don’t detect because it didn’t cause the program to crash. We try to avoid these cases by using significant enough inputs that an overflow will cause a crash but this can’t be guaranteed. Similarly, when fuzzing format strings we try to use %n and %s as these are the most likely to lead to a crashed state.


#### Coverage

The coverage metric was a simple implementation where the children of an input that discovered a new path are given a bump in priority to be run. We didn’t look at improving this or utilizing more advanced metrics as we didn’t come up with any examples where we a more effective coverage tactic. Thus, most of our attempts at the problem rely on different types of ad-hoc mutations guided by this one metric.


#### Python

You would think that Python would be bad because it’s slow, but Python is **actually **bad because it has no types; so you don’t end up making well-defined interfaces between pieces of code and don’t decide when you’re returning a single object or a list, etc. then your program breaks in odd places.


#### Strategies

We also don’t do a bunch of things that we planned on doing, because software engineering is hard:



*   If we mutate an input by adding a big string, stop mutating the input  (since that would be pretty slow and pointless)
*   Being able to put in one strategy like ‘add a list of entries’ and have the mutator do only that strategy. Instead, for some strategies, we end up picking an arbitrary strategy at random, because that’s how we did it in the midpoint.

Our thing is also non-deterministic. We had some software engineering problems making it pseudo-random, so our program is actually random and sometimes takes a long time to work.
