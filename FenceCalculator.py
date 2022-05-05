fence_length = 75
length_per_vinyl = 8
vinyl_cost = 110.01
post_cost = 38 + 3.48
length_per_post = 5 / 12

current_fence_length = fence_length - (length_per_post * 2)
fence_count = 0
post_count = 2
while current_fence_length > 0:
    fence_count += 1
    post_count += 1
    current_fence_length -= length_per_vinyl
    current_fence_length -= length_per_post

total_vinyl_cost = fence_count * vinyl_cost
total_post_cost = post_count * post_cost
total_fence_cost = total_vinyl_cost + total_post_cost + 600
print(f"Fences: {fence_count}\nCost: {total_vinyl_cost}")
print(f"Posts: {post_count}\nCost: {total_post_cost}")
print(f"Final fence length: {current_fence_length}\nCost: {total_fence_cost}")
