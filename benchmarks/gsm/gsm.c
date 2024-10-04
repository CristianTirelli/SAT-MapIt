#include <stdio.h>

#define GSM_ABS(a) ((a) < 0 ? ((a) == MIN_WORD ? MAX_WORD : -(a)) : (a))
#define MIN_WORD ((-32767) - 1)
#define MAX_WORD (32767)

int gsm(int *d)
{

    int dmax = 0;
    int temp = 0;

#pragma cgra acc
    for (int k = 0; k <= 39; k++)
    {
        temp = d[k];
        temp = GSM_ABS(temp);
        if (temp > dmax)
            dmax = temp;
    }

    return dmax;
}

int main()
{

    int d[50];
    gsm(d);
}