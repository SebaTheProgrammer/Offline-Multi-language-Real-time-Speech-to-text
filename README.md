# Offline-Multi-language-Real-time-Speech-to-text
Made in my short summer internship at the Belgian Defence, XR-Labs.

# Info:
There are two variations, as you can see, one with a threaded pipeline to communicate with a c# program/pipeline, and just a normal python script that works alone.

I really recommend using CUDA and not just on the cpu. That way it will be a lot, but a lot faster.

This was designed to run next to their program, so that's why it is heavily threaded. But if you find any improvements, please let me know :).

# Deeper logic:

- Chunck loading:

First of all, how does voice recognition works? In simple terms, you record your audio and let an advanced ai/program decipher the words.
The thing is, deciphering is a heavy task. That is the reason that I splitsed it in 10 chucks that continuesly get's recorded and deciphered.

It didn't matter for my end user in which order the words get deciphered. (Example: if it takes a lot of time for the first one, but the second chunck is shorter, the second chunck's string get passed first.)

That way stands this program never still.

- String Comparison:

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

