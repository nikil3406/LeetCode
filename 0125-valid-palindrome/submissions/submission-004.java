/*
 * LeetCode Submission
 * Submission ID: 2184365768
 * Status: Accepted
 * Language: java
 * Runtime: 4 ms
 * Memory: 43.7 MB
 * Submitted: 2026-10-29 02:42:19 UTC
 */
/*
 * INTUITION
 * This solution uses a two-pointer approach to check if the string is a palindrome without spending extra space on a cleaned string. Two indices start at opposite ends of the string and move towards the center. Non-alphanumeric characters are skipped dynamically, and valid characters are compared in a case-insensitive manner.
 *
 * APPROACH
 * 1. Initialize a left pointer `l` to 0 and a right pointer `r` to the last index of string `s`.
 * 2. Enter a `while` loop that runs as long as `l < r`.
 * 3. Check if the character at index `l` is alphanumeric; if not, increment `l` and skip to the next loop iteration.
 * 4. Check if the character at index `r` is alphanumeric; if not, decrement `r` and skip to the next loop iteration.
 * 5. Convert both valid characters at `l` and `r` to lowercase and compare them.
 * 6. If the characters do not match, return `false`.
 * 7. If they match, increment `l` and decrement `r` to move both pointers inward.
 * 8. If the loop terminates without finding a mismatch, return `true`.
 *
 * WHY IT WORKS
 * The algorithm filters out non-alphanumeric characters on the fly by advancing the left pointer or retreating the right pointer whenever an invalid character is encountered. Converting matching positions to lowercase satisfies the case-insensitivity rule. Because palindromes require mirror symmetry from the outside in, checking equality at every pair of valid characters guarantees the cleaned string reads the same forward and backward.
 *
 * COMPLEXITY
 * Time Complexity: O(n), where n is the length of the string `s`. In the worst case, every character in the string is checked once by either the left or right pointer.
 * Space Complexity: O(1) auxiliary space, as the operation works directly on the original string using only two integer pointers.
 */

class Solution {
    public boolean isPalindrome(String s) {
        int l = 0;
        int r = s.length() - 1;

        while (l < r) {
            if (!Character.isLetterOrDigit(s.charAt(l))) {
                l++;
                continue;
            }

            if (!Character.isLetterOrDigit(s.charAt(r))) {
                r--;
                continue;
            }

            if (Character.toLowerCase(s.charAt(l)) !=
                Character.toLowerCase(s.charAt(r))) {
                return false;
            }

            l++;
            r--;
        }

        return true;
    }
}
