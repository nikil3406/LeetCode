/*
 * LeetCode Submission
 * Submission ID: 2183553926
 * Status: Wrong Answer
 * Language: java
 * Runtime: N/A
 * Memory: N/A
 * Submitted: 2026-10-28 03:08:41 UTC
 */
/*
 * INTUITION
 * The solution repeatedly extracts the last digit of the input integer using modulo operations and appends it to a running reversed variable by multiplying the accumulator by 10. To prevent standard 32-bit integer overflow without using 64-bit types, it includes a threshold check inside the loop before shifting digits. It continues this process until all digits from the input number are consumed.
 *
 * APPROACH
 * 1. Initialize an integer variable `rev` to 0 to hold the reversed result.
 * 2. Enter a `while` loop that executes as long as `x` is not equal to 0.
 * 3. Check if `x` exceeds `Integer.MAX_VALUE / 10` or is less than `Integer.MIN_VALUE / 10`; if so, return 0 to prevent numerical overflow.
 * 4. Extract the last digit of `x` using `x % 10` and append it to `rev` using `(rev * 10) + (x % 10)`.
 * 5. Remove the last digit from `x` using integer division `x /= 10`.
 * 6. Return `rev` after all digits have been processed.
 *
 * WHY IT WORKS
 * The modulo operation `x % 10` retrieves the rightmost digit of `x` in each step, regardless of whether `x` is positive or negative in Java. Multiplying `rev` by 10 shifts its current digits to the left by one decimal place, making room to add the newly extracted digit. Integer division `x /= 10` truncates the processed digit from `x`, eventually driving `x` to 0 and ending the reversal process.
 *
 * COMPLEXITY
 * Time Complexity: O(log10(|x|)) — The number of loop iterations corresponds to the number of decimal digits in `x`, which is at most 10 digits for a 32-bit signed integer.
 * Space Complexity: O(1) — The algorithm uses a fixed number of primitive integer variables (`rev`) requiring constant extra space.
 */

class Solution {
    public int reverse(int x) {
        int rev = 0;
        while(x!=0){
            if(x>Integer.MAX_VALUE/10 || x<Integer.MIN_VALUE/10) return 0;
            rev = (rev*10)+(x%10);
            x/=10;
        }
        return rev;
    }
}
