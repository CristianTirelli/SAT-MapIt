#include <stdio.h>
#include <math.h>

unsigned ReverseBits(unsigned index, unsigned NumBits)
{
    unsigned i, rev;

#pragma cgra acc
    for (i = rev = 0; i < NumBits; i++)
    {
        rev = (rev << 1) | (index & 1);
        index >>= 1;
    }

    return rev;
}

int main()
{

    return 0;
}