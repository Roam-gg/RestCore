from roamrs import Cog, route, Method
import roamrs

def test_route_creation():
    class TestCog(Cog):
        @route('/test', Method.GET)
        async def test_func(self, response):
            print('a')
    t = TestCog()
    assert len(t._routes) == 1
    for r in t._routes:
        assert isinstance(r, roamrs.cog.RouteHolder)
    r = t._routes[0]
    assert r.path == '/test'
    assert r.method == Method.GET
    print(r.cog)
    print(t)
    assert r.cog == t
    assert r.func == t.test_func
