#include <stdio.h>

void sha_transform(int W[])
{
#pragma cgra acc
	for (int i = 16; i < 80; ++i)
		W[i] = W[i - 3] ^ W[i - 8] ^ W[i - 14] ^ W[i - 16];
}

int main()
{

	int W[80];
	sha_transform(W);
}
