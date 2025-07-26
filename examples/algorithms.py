"""
Algorithm Functions Example
==========================

A collection of algorithm implementations that can be converted to API endpoints.
This demonstrates various algorithmic problems and solutions.
"""

from typing import List, Dict, Optional, Tuple, Set
import heapq
from collections import defaultdict, deque


def binary_search(arr: List[int], target: int) -> int:
    """Binary search to find target in sorted array. Returns index or -1 if not found."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def bubble_sort(arr: List[int]) -> List[int]:
    """Sort array using bubble sort algorithm."""
    arr_copy = arr.copy()
    n = len(arr_copy)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr_copy[j] > arr_copy[j + 1]:
                arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
    
    return arr_copy


def quick_sort(arr: List[int]) -> List[int]:
    """Sort array using quick sort algorithm."""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(arr: List[int]) -> List[int]:
    """Sort array using merge sort algorithm."""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left: List[int], right: List[int]) -> List[int]:
    """Merge two sorted arrays."""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def two_sum(nums: List[int], target: int) -> List[int]:
    """Find two numbers in array that add up to target. Returns indices."""
    seen = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    
    return []


def max_sum_subarray_k(arr: List[int], k: int) -> int:
    """Find maximum sum of subarray of size k using sliding window."""
    if k > len(arr):
        return 0
    
    # Calculate sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    # Slide the window
    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)
    
    return max_sum


def longest_substring_without_repeating(s: str) -> int:
    """Find length of longest substring without repeating characters."""
    char_map = {}
    left = 0
    max_length = 0
    
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length


def valid_parentheses(s: str) -> bool:
    """Check if string has valid parentheses."""
    stack = []
    brackets = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack.pop() != brackets[char]:
                return False
    
    return len(stack) == 0


def fibonacci_dynamic(n: int) -> int:
    """Calculate nth Fibonacci number using dynamic programming."""
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]


def climb_stairs(n: int) -> int:
    """Find number of ways to climb n stairs (1 or 2 steps at a time)."""
    if n <= 2:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]


def coin_change(coins: List[int], amount: int) -> int:
    """Find minimum number of coins needed to make amount."""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1


def longest_common_subsequence(text1: str, text2: str) -> int:
    """Find length of longest common subsequence between two strings."""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]


def word_break(s: str, word_dict: List[str]) -> bool:
    """Check if string can be segmented into words from dictionary."""
    word_set = set(word_dict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[len(s)]


def find_duplicates(nums: List[int]) -> List[int]:
    """Find all duplicates in array where numbers are 1 to n."""
    result = []
    
    for num in nums:
        index = abs(num) - 1
        if nums[index] < 0:
            result.append(abs(num))
        else:
            nums[index] = -nums[index]
    
    return result


def rotate_array(nums: List[int], k: int) -> List[int]:
    """Rotate array to the right by k steps."""
    n = len(nums)
    k = k % n
    
    # Reverse entire array
    nums.reverse()
    
    # Reverse first k elements
    nums[:k] = reversed(nums[:k])
    
    # Reverse remaining elements
    nums[k:] = reversed(nums[k:])
    
    return nums


def find_missing_number(nums: List[int]) -> int:
    """Find missing number in array containing 0 to n."""
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    return expected_sum - actual_sum


def single_number(nums: List[int]) -> int:
    """Find single number in array where all others appear twice."""
    result = 0
    for num in nums:
        result ^= num
    return result


def majority_element(nums: List[int]) -> int:
    """Find element that appears more than n/2 times (Boyer-Moore algorithm)."""
    count = 0
    candidate = None
    
    for num in nums:
        if count == 0:
            candidate = num
        count += (1 if num == candidate else -1)
    
    return candidate


def group_anagrams(strs: List[str]) -> List[List[str]]:
    """Group strings that are anagrams of each other."""
    anagram_groups = defaultdict(list)
    
    for s in strs:
        # Sort characters to create key
        key = ''.join(sorted(s))
        anagram_groups[key].append(s)
    
    return list(anagram_groups.values())


def top_k_frequent(nums: List[int], k: int) -> List[int]:
    """Find top k most frequent elements."""
    # Count frequencies
    frequency = defaultdict(int)
    for num in nums:
        frequency[num] += 1
    
    # Use min heap to keep top k elements
    heap = []
    for num, freq in frequency.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)
    
    return [num for freq, num in heap]


def product_except_self(nums: List[int]) -> List[int]:
    """Return array where each element is product of all elements except self."""
    n = len(nums)
    result = [1] * n
    
    # Calculate left products
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]
    
    # Calculate right products
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    
    return result


def max_profit(prices: List[int]) -> int:
    """Find maximum profit from buying and selling stock once."""
    if not prices:
        return 0
    
    min_price = prices[0]
    max_profit = 0
    
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    
    return max_profit


def is_valid_sudoku(board: List[List[str]]) -> bool:
    """Check if 9x9 Sudoku board is valid."""
    # Check rows
    for row in board:
        if not is_valid_unit(row):
            return False
    
    # Check columns
    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if not is_valid_unit(column):
            return False
    
    # Check 3x3 boxes
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            box = []
            for row in range(i, i + 3):
                for col in range(j, j + 3):
                    box.append(board[row][col])
            if not is_valid_unit(box):
                return False
    
    return True


def is_valid_unit(unit: List[str]) -> bool:
    """Check if a unit (row, column, or box) is valid."""
    seen = set()
    for cell in unit:
        if cell != '.':
            if cell in seen:
                return False
            seen.add(cell)
    return True


def spiral_order(matrix: List[List[int]]) -> List[int]:
    """Return elements of matrix in spiral order."""
    if not matrix:
        return []
    
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Traverse right
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1
        
        # Traverse down
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        
        # Traverse left
        if top <= bottom:
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1
        
        # Traverse up
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    
    return result


def generate_parentheses(n: int) -> List[str]:
    """Generate all valid combinations of n pairs of parentheses."""
    def backtrack(open_count, close_count, current):
        if len(current) == 2 * n:
            result.append(current)
            return
        
        if open_count < n:
            backtrack(open_count + 1, close_count, current + '(')
        
        if close_count < open_count:
            backtrack(open_count, close_count + 1, current + ')')
    
    result = []
    backtrack(0, 0, '')
    return result


def subsets(nums: List[int]) -> List[List[int]]:
    """Generate all possible subsets of array."""
    def backtrack(start, current):
        result.append(current[:])
        
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()
    
    result = []
    backtrack(0, [])
    return result


def permutations(nums: List[int]) -> List[List[int]]:
    """Generate all permutations of array."""
    def backtrack(first):
        if first == len(nums):
            result.append(nums[:])
            return
        
        for i in range(first, len(nums)):
            nums[first], nums[i] = nums[i], nums[first]
            backtrack(first + 1)
            nums[first], nums[i] = nums[i], nums[first]
    
    result = []
    backtrack(0)
    return result 