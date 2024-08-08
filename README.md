# Offline-Multi-language-Real-time-Speech-to-text
Made in my short summer internship at the Belgium Defence, XR-Labs.

# Info:
There are two variations, as you can see, one with a threaded pipeline to communicate with a c# program/pipeline, and just a normal python script that works alone.

You can easily change the language and model (of faster whisper) to finetune it for your liking.

I really recommend using CUDA and not just on the cpu. That way it will be a lot, but a lot faster.

This was designed to run next to their game, so it should be pretty optimized. But if you find any improvements, please let me know :).

# Deeper logic:

String Comparison:

After a word is recognized by the Python script, we need to check if that word or sentence corresponds to a specific function. 
To address this problem, I used the Levenshtein distance. (https://en.wikipedia.org/wiki/Levenshtein_distance)

![Levenshtein_distance_animation](https://github.com/user-attachments/assets/2f971679-5836-47ce-8cdc-cc4b5836ba52)

