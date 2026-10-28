/*
 * LeetCode Submission
 * Submission ID: 2183545246
 * Status: Accepted
 * Language: java
 * Runtime: 3 ms
 * Memory: 45.8 MB
 * Submitted: 2026-10-28 02:48:09 UTC
 */
/*
 * INTUITION
 * This solution simulates element-by-element addition of two numbers represented as linked lists, moving from least significant digit to most significant digit. Since the digits are already given in reverse order, addition can be performed directly starting from the heads of both lists. A dummy node is used to build the result list easily while maintaining a carry variable across loop iterations.
 *
 * APPROACH
 * 1. Create a dummy sentinel node named temp and set a pointer current to temp, along with an integer variable carry initialized to 0.
 * 2. Traverse the lists using a while loop that runs as long as l1 is not null, l2 is not null, or carry is non-zero.
 * 3. Initialize sum with the current carry value, add l1.val if l1 is not null, and add l2.val if l2 is not null, advancing l1 and l2 to their next nodes accordingly.
 * 4. Calculate the new carry as sum / 10 and update sum to sum % 10 for the current digit.
 * 5. Create a new ListNode with value sum, attach it to current.next, and move current to current.next.
 * 6. Return temp.next, which points to the real head of the generated sum linked list.
 *
 * WHY IT WORKS
 * The reverse-order linked list structure aligns directly with traditional digit-by-digit addition starting from the ones place. Using the combined condition `l1 != null || l2 != null || carry != 0` ensures that lists of different lengths are fully traversed and any extra carry at the end creates a final output node. The dummy head node prevents special handling when inserting the first element.
 *
 * COMPLEXITY
 * Time Complexity: O(max(N, M)), where N and M are the lengths of l1 and l2 respectively. The loop runs at most max(N, M) + 1 times.
 * Space Complexity: O(max(N, M)), as a new linked list of length at most max(N, M) + 1 is instantiated to hold the sum digits.
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
