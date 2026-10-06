def role(request):
    u = request.user
    if not u.is_authenticated:
        return {"role": "guest"}
    p = getattr(u, "profile", None)
    return {"role": p.role if p else "staff"}
