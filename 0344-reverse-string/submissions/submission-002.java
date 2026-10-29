/*
 * LeetCode Submission
 * Submission ID: 2184361883
 * Status: Accepted
 * Language: java
 * Runtime: 1 ms
 * Memory: 47.6 MB
 * Submitted: 2026-10-29 02:31:06 UTC
 */
/*
 * INTUITION
 * To reverse an array of characters in-place, the solution employs a classic two-pointer approach. By initializing one pointer at the start of the string and another at the end, the algorithm systematically swaps opposing elements. Moving the pointers toward the center ensures every character is mirrored across the middle of the array without allocating additional memory.
 *
 * APPROACH
 * 1. Perform an initial safety check: if the array length is 0, return immediately.
 * 2. Initialize a left pointer `l` to 0 and a right pointer `r` to `s.length - 1`.
 * 3. Loop while `r > l`, ensuring the pointers have not met or crossed.
 * 4. Temporarily store the character at index `l` in a variable `c`.
 * 5. Assign the character at index `r` to index `l`, and assign `c` to index `r`.
 * 6. Increment `l` by 1 and decrement `r` by 1 to move inward.
 * 7. Return once the loop condition fails and all pairs are swapped.
 *
 * WHY IT WORKS
 * Reversing a sequence means moving the element at index `i` to index `N - 1 - i`. Swapping the outer pair of characters puts both in their correct final positions for the reversed string. Repeating this process for all outer pairs until the pointers meet in the middle guarantees that every element is relocated to its mirrored position.
 *
 * COMPLEXITY
 * Time Complexity: O(N), where N is the length of the array `s`. The loop runs N / 2 times, performing O(1) swap operations per iteration.
 * Space Complexity: O(1), as the reversal is performed in-place using only a few primitive variables (`l`, `r`, and `c`).
 */

class Solution {
    public void reverseString(char[] s) {
        if(s.length == 0) return;

        int l = 0;
        int r = s.length-1;

        while(r>l){
            char c = s[l];
            s[l] = s[r];
            s[r] = c;
            l++;
            r--;
        }
        return;
    }
}
