class Strategy:
    NO_STRATEGY = 'none'
    ADD_DICTS = 'add_members_to_dict'
    INCREMENT = 'increment'
    DECREMENT = 'decrement'
    MAX = 'max' #big todo: split into different strategies
    MIN = 'min'
    MAKE_ZERO = 'make_zero'
    BIT_FLIP = 'bit_flip'
    BYTE_FLIP = 'byte_flip'
    NAN = 'na'
    ZERO = 'zero'
    FORMAT = 'format'
    NON_ASCII = 'non_ascii'


    members_to_add_to_dict = 100


    #towards the start of the time running the program, and others later
    MEDIUM_STRATEGIES = [MAX, MIN, MAKE_ZERO, ZERO, NAN, NON_ASCII]
    #eventually we'll make the mid strategies different from early strategies
    #the idea is that we do risker strategies later.
    EARLY_STRATEGIES = [BIT_FLIP, BYTE_FLIP, INCREMENT, DECREMENT, MAX, MIN]+MEDIUM_STRATEGIES


    LATE_STRATEGIES = [FORMAT, ADD_DICTS, NO_STRATEGY]


    # STRATEGIES = [NO_STRATEGY, ADD_DICTS] 
    
