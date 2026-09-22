/*
 * LeetCode Submission
 * Submission ID: 1925092769
 * Status: Accepted
 * Language: java
 * Runtime: 1 ms
 * Memory: 46.7 MB
 * Submitted: 2026-02-20 06:26:57 UTC
 */
/*
 * INTUITION
 * The input numbers are given in reverse order, meaning the heads of the linked lists contain the least significant digits. This directly matches standard manual addition, where you sum digits from right to left while maintaining a carry. The solution processes both lists simultaneously node by node, calculating digit sums and propagating carries to construct the resulting linked list.
 *
 * APPROACH
 * 1. Create a dummy node named temp to act as the start of the output list, set a pointer current to temp, and set an integer carry to 0.
 * 2. Enter a loop that runs as long as l1 is not null, l2 is not null, or carry is non-zero.
 * 3. Initialize sum with the current carry value.
 * 4. If l1 is not null, add its value to sum and move l1 to its next node.
 * 5. If l2 is not null, add its value to sum and move l2 to its next node.
 * 6. Compute the new carry by dividing sum by 10, and compute the digit to store by taking sum modulo 10.
 * 7. Create a new ListNode with the calculated single-digit sum, set it as current.next, and move current forward.
 * 8. Return temp.next, which points to the actual head of the resulting sum list.
 *
 * WHY IT WORKS
 * Because the lists are reversed, the traversal naturally moves from the least significant digit to the most significant digit. By tracking the carry across iterations, the code accurately mimics column-by-column decimal addition. Including carry != 0 in the loop condition guarantees that any final carry-over generates a new node at the end of the list, even after both input lists have been fully traversed. Using a dummy node avoids writing extra conditional logic for initializing the head of the output list.
 *
 * COMPLEXITY
 * Time Complexity: O(max(N, M)), where N is the length of l1 and M is the length of l2. The while loop runs at most max(N, M) + 1 times because it processes each node from both lists once, plus an optional extra iteration for a remaining carry.
 *
 * Space Complexity: O(max(N, M)), as a new linked list is constructed to store the result, requiring at most max(N, M) + 1 new nodes.
 */

/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode temp = new ListNode(0);
        ListNode current = temp;
        int carry = 0;

        while(l1!=null || l2!=null || carry!=0){
            int sum = carry;
            if(l1!=null){
                sum+=l1.val;
                l1=l1.next;
            }
            if(l2!=null){
                sum+=l2.val;
                l2=l2.next;
            }

            carry = sum/10;
            sum=sum%10;
            current.next = new ListNode(sum);
            current = current.next;
        }
        return temp.next;
    }
}
