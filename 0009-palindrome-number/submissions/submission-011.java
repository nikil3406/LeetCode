/*
 * LeetCode Submission
 * Submission ID: 2183559030
 * Status: Accepted
 * Language: java
 * Runtime: 15 ms
 * Memory: 45.5 MB
 * Submitted: 2026-10-28 03:20:27 UTC
 */
/*
 * INTUITION
 * This solution checks if an integer is a palindrome by reversing only its second half and comparing it directly to the remaining first half. It first filters out edge cases, such as negative numbers and non-zero numbers ending in zero, which can never be palindromes. Reversing only half of the digits prevents integer overflow that might occur if the entire number were reversed.
 *
 * APPROACH
 * 1. Return false immediately if x is negative, or if x ends in 0 while not being 0 itself.
 * 2. Initialize an integer variable res to 0 to store the reversed right half of the number.
 * 3. Run a while loop as long as x is greater than res. In each iteration, pop the last digit of x using x % 10, append it to res, and drop the last digit from x using integer division by 10.
 * 4. After the loop, return true if x equals res (for numbers with an even number of digits) or if x equals res / 10 (for numbers with an odd number of digits where the middle digit is pushed into res).
 *
 * WHY IT WORKS
 * The algorithm processes digits from right to left and builds the reversed second half in res until res is greater than or equal to x, indicating that half of the digits have been processed. For an even-digit palindrome, the remaining original left half (x) will match the reversed right half (res). For an odd-digit palindrome, the middle digit ends up as the trailing digit of res, so dividing res by 10 removes the middle digit and allows a direct comparison with x.
 *
 * COMPLEXITY
 * Time Complexity: O(log10(x)) because the input number is divided by 10 in each iteration, resulting in processing only half of the digits of x.
 * Space Complexity: O(1) as it uses a constant amount of extra memory for a single variable res.
 */

class Solution {
    public boolean isPalindrome(int x) {
        if(x<0 || (x%10 ==0 && x!=0)){
            return false;
        }

        int res = 0;
        while(x>res){
            res = res*10 + x%10;
            x= x/10;
        }
        return x==res || x == res/10;
    }
}
