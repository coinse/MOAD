#include <stdio.h>
int isletter(char c);
int main(int argc, char *argv[])
{
    int characters;
    int lines;
    int inword;
    int words;
    char c;
    characters = 0;printf("\nORBS:%d:%d:%s:%d\n", 10, 5, "characters", characters);
    inword = 0;printf("\nORBS:%d:%d:%s:%d\n", 11, 5, "inword", inword);
    words = 0;printf("\nORBS:%d:%d:%s:%d\n", 12, 5, "words", words);
    printf("\nORBS:%d:%d:%s:%d\n", 13, 25, "c", c);while (scanf("%c", &c) == 1)
    {
        printf("\nORBS:%d:%d:%s:%d\n", 15, 22, "characters", characters);characters = characters + 1;printf("\nORBS:%d:%d:%s:%d\n", 15, 9, "characters", characters);
        printf("\nORBS:%d:%d:%s:%d\n", 16, 13, "c", c);if (c == '\n')
        {
            printf("\nORBS:%d:%d:%s:%d\n", 18, 21, "lines", lines);lines = lines + 1;printf("\nORBS:%d:%d:%s:%d\n", 18, 13, "lines", lines);
        }
        printf("\nORBS:%d:%d:%s:%d\n", 20, 22, "c", c);if (isletter(c))
        {
            printf("\nORBS:%d:%d:%s:%d\n", 22, 17, "inword", inword);if (inword == 0)
            {
                printf("\nORBS:%d:%d:%s:%d\n", 24, 25, "words", words);words = words + 1;printf("\nORBS:%d:%d:%s:%d\n", 24, 17, "words", words);
                inword = 1;printf("\nORBS:%d:%d:%s:%d\n", 25, 17, "inword", inword);
            }
        }
        else
        {
            inword = 0;printf("\nORBS:%d:%d:%s:%d\n", 30, 13, "inword", inword);
        }
    printf("\nORBS:%d:%d:%s:%d\n", 13, 25, "c", c);}
}
int isletter(char c)
{
    printf("\nORBS:%d:%d:%s:%d\n", 36, 19, "c", c);printf("%c ", c);
    printf("\nORBS:%d:%d:%s:%d\n", 37, 11, "c", c);if (((c >= 'A') && (c <= 'Z'))
        || ((c >= 'a') && (c <= 'z')))
    {
        return 1;
    }
    else
    {
        return 0;
    }
}