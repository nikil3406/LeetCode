/*
 * LeetCode Submission
 * Submission ID: 2184366053
 * Status: Accepted
 * Language: java
 * Runtime: 3 ms
 * Memory: 43.9 MB
 * Submitted: 2026-10-29 02:43:10 UTC
 */
/*
 * INTUITION
 * This solution uses a two-pointer technique to check for a palindrome in-place without generating a new filtered string. Two pointers start at opposite ends of the string and move toward the center. Non-alphanumeric characters are skipped dynamically during iteration, while valid characters are compared in a case-insensitive manner.
 *
 * APPROACH
 * 1. Initialize two pointers: l at the beginning (index 0) and r at the end (s.length() - 1) of the string.
 * 2. Loop as long as l is less than r.
 * 3. Fetch the character at index l as left and the character at index r as right.
 * 4. Check if left is not a letter or digit; if so, increment l to skip it.
 * 5. Else, check if right is not a letter or digit; if so, decrement r to skip it.
 * 6. If both characters are alphanumeric, convert both to lowercase using Character.toLowerCase() and compare them.
 * 7. If the lowercase characters do not match, return false immediately.
 * 8. If they match, increment l and decrement r to move toward the center.
 * 9. Return true if the loop finishes without finding any mismatched characters.
 *
 * WHY IT WORKS
 * The algorithm filters out invalid characters on the fly by advancing individual pointers whenever a non-alphanumeric character is encountered. When both pointers land on valid characters, case-insensitive equality ensures that uppercase and lowercase versions of the same letter are treated identically. Since the pointers move inward symmetrically and cover all valid character pairs, verifying equality across all pairs guarantees the string reads the same forward and backward.
 *
 * COMPLEXITY
 * Time Complexity: O(n), where n is the length of the string s. Each character in the string is visited at most once by either the left or right pointer.
 * Space Complexity: O(1), as the algorithm operates directly on the input string using a fixed number of primitive variables, requiring no additional data structures.
 */

class Solution {
    public boolean isPalindrome(String s) {
        int l = 0, r = s.length() - 1;

        while (l < r) {
            char left = s.charAt(l);
            char right = s.charAt(r);

            if (!Character.isLetterOrDigit(left)) {
                l++;
            } else if (!Character.isLetterOrDigit(right)) {
                r--;
            } else {
                if (Character.toLowerCase(left) !=
                    Character.toLowerCase(right)) {
                    return false;
                }

                l++;
                r--;
            }
        }

        return true;
    }
}
