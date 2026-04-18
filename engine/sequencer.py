from collections import defaultdict, deque

def sequence_schemes(schemes_list):
    # topological sort of schemes
    adj = defaultdict(list)
    indegree = {s.scheme_id: 0 for s in schemes_list}
    
    for s in schemes_list:
        for pre in s.prerequisites:
            req_id = pre["scheme"]
            if req_id in indegree:
                adj[req_id].append(s.scheme_id)
                indegree[s.scheme_id] += 1
                
    q = deque([k for k, v in indegree.items() if v == 0])
    order = []
    
    while q:
        curr = q.popleft()
        order.append(curr)
        for nxt in adj[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)
                
    # any loose loops get appended at end
    remaining = set(indegree.keys()) - set(order)
    order.extend(list(remaining))
    
    # Return dict mapping scheme_id to its 1-indexed order position
    return {sch: idx+1 for idx, sch in enumerate(order)}
