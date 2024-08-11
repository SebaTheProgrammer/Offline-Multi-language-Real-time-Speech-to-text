# Offline-Multi-language-Real-time-Speech-to-text
Made in my short summer internship at the Belgium Defence, XR-Labs.
It uses the faster_whisper of openAI, https://github.com/openai/whisper 

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

Edit distance matrix for two words using cost of substitution as 1 and cost of deletion or insertion as 0.5.

    private static int LevenshteinDistance(string s, string t)
    {
        int[,] d = new int[s.Length + 1, t.Length + 1];

        for (int i = 0; i <= s.Length; i++)
            d[i, 0] = i;
        for (int j = 0; j <= t.Length; j++)
            d[0, j] = j;

        for (int i = 1; i <= s.Length; i++)
        {
            for (int j = 1; j <= t.Length; j++)
            {
                int cost = (t[j - 1] == s[i - 1]) ? 0 : 1;

                d[i, j] = Math.Min(
                    Math.Min(d[i - 1, j] + 1, d[i, j - 1] + 1),
                    d[i - 1, j - 1] + cost);
            }
        }

        return d[s.Length, t.Length];
    }
    
    private static double SimilarityPercentage(string s, string t)
    {
        int distance = LevenshteinDistance(s, t);
        int maxLength = Math.Max(s.Length, t.Length);
        return (1.0 - (double)distance / maxLength) * 100;
    }
    
    private static bool IsAtLeastXPercentSimilar(string s, string t, float procentequal = 50.0f)
    {
        if (s.Length > 0)
        {
            char lastChar = s[s.Length - 1];
            if (lastChar == '.' || lastChar == '!' || lastChar == '?')
            {
                s = s.Substring(0, s.Length - 1);
            }

            if (s.Contains(t) || t.Contains(s))
                return true;

            return SimilarityPercentage(s, t) >= procentequal;
        }

        return false;
    }

