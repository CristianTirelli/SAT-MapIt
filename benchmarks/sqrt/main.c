#include <stdint.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

#define TEST_LENGTH 10

uint16_t isqrt32(uint32_t* in_ptr);


int main(int argc, char** argv) {
	uint32_t mathSqrt, mySqrt;
	uint32_t errors = 0;

	srand(time(NULL));

/*	for (int8_t i = 0; i < TEST_LENGTH; ++i) {
		uint32_t test_val = rand()%32768;
		mathSqrt = sqrt((double)test_val);
		mySqrt   = isqrt32(&test_val);

		if (mathSqrt != mySqrt) {
			printf("%d: sqrt(%d) = %d != %d\n", i, test_val, mathSqrt, mySqrt);
			errors++;
		} else {
			printf("%d: sqrt(%d) = %d = %d\n", i, test_val, mathSqrt, mySqrt);
		}
	}

	if(errors==0) {
		printf("SUCCESS: no error!\n");
		return EXIT_SUCCESS;
	} else {
		printf("FAILURE: %d errors out of %d tested values!\n", errors, TEST_LENGTH);
		return EXIT_FAILURE;
	}
*/
	return EXIT_FAILURE;
}

uint16_t isqrt32(uint32_t* in_ptr) 
{
	uint16_t mask = 1<<14;
	uint16_t result = 0;
	uint16_t temp = 0;

	if(*in_ptr < 0) return 0;
	while(mask)
	{
		temp = result | mask;
		if((((uint32_t)temp)*((uint32_t)temp)) <= ((uint32_t)(*in_ptr)))
			result = temp;
		mask >>= 1;
	}
	return result;
}
