/*
 * LeetCode Submission
 * Submission ID: 2183554822
 * Status: Accepted
 * Language: java
 * Runtime: 1 ms
 * Memory: 41.9 MB
 * Submitted: 2026-10-28 03:10:44 UTC
 */
/*
 * INTUITION
 * This solution reverses the integer digit by digit using basic arithmetic operations. It pops the last digit off the input integer using modulo division and pushes it onto the reversed result. Before multiplying the reversed total by 10, it checks whether the operation would cause a 32-bit signed integer overflow, returning 0 immediately if an overflow is detected.
 *
 * APPROACH
 * 1. Initialize a variable rev to 0 to store the accumulating reversed integer.
 * 2. Enter a while loop that runs as long as x is not equal to 0.
 * 3. Check if rev is strictly greater than Integer.MAX_VALUE / 10 or strictly less than Integer.MIN_VALUE / 10; if either condition is met, return 0 because multiplying rev by 10 would result in an integer overflow.
 * 4. Update rev by multiplying it by 10 and adding the last digit of x (computed via x % 10).
 * 5. Truncate the last digit of x by performing integer division (x /= 10).
 * 6. Once all digits are processed and x becomes 0, return rev.
 *
 * WHY IT WORKS
 * In integer arithmetic, x % 10 yields the rightmost digit, and x / 10 removes it. Multiplying rev by 10 shifts all existing reversed digits one place to the left, allowing the new digit to be added at the ones place. Checking rev against Integer.MAX_VALUE / 10 and Integer.MIN_VALUE / 10 prior to multiplication ensures that rev * 10 never exceeds 32-bit limits, strictly adhering to the 32-bit constraint without needing a 64-bit integer type.
 *
 * COMPLEXITY
 * Time Complexity: O(log10(|x|)) because the loop executes once for every base-10 digit in x, which is at most 10 times for a 32-bit signed integer.
 * Space Complexity: O(1) because it only uses a single fixed-size variable rev to store the result.
 */

class Solution {
    public int reverse(int x) {
        int rev = 0;
        while(x!=0){
            if(rev>Integer.MAX_VALUE/10 || rev<Integer.MIN_VALUE/10) return 0;
            rev = (rev*10)+(x%10);
            x/=10;
        }
        return rev;
    }
}
