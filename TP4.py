from SPARQLWrapper import SPARQLWrapper, JSON
import math
import sys

# CONST
Z = 1.96

# GETS A WRAPPER TO DO A QUERY IN A CERTAIN FORMAT
def do_query(w, q, f):
        w.setQuery(q)

        w.setReturnFormat(f)

        try:
        	results = w.query().convert()
        except Exception as e:
        	sys.exit("Couldn't make request")

        return results

# GETS A LIST OF ALL THE CLASSES IN THE RDF
def get_classes(r):
	return [c["class"]["value"] for c in r["results"]["bindings"]]

# COMPUTES THE BINOMIAL PROPORTION
def binomial_proportion(m, s, nb=0):
	if nb == 0:
		if m != 0:
			return s/m
		return False
	elif nb == 1:
		if m + 4 != 0:
			return (s + 2) / (m + 4)
		else:
			return False

def avg_of_extremes(_p, _Z, _m):
	_p_prime = _p + (_Z * math.sqrt((_p * (1 - _p)) / (_m)))
	return _p_prime

# INITIALIZING VARIABLES
sparql_endpoint = "http://dblp.l3s.de/d2r/sparql"
sparql = SPARQLWrapper(sparql_endpoint)

# QUERY TO GET LIST OF DISTINCT CLASSES
classes_query = "SELECT DISTINCT ?class WHERE { ?_ a ?class . }"

# GETTING THE LIST OF DISCTINCT CLASSES IN THE RDF
classes = get_classes(do_query(sparql, classes_query, JSON))
print("########-CLASSES-########")
for c in classes:
	print(c)

# X IN C
# FOR EVERY CLASS NAME C WE COMPUTE M
print("########-X IN C-########")
m = {};
for c in classes:
	nb_x_in_class_query = "SELECT (COUNT(DISTINCT ?x) AS ?m) WHERE { ?x a %s . }" % ("<" + c + ">")
	m[c] = int(do_query(sparql, nb_x_in_class_query, JSON)["results"]["bindings"][0]["m"]["value"])
	print(m[c])

# X IN C . X IN D
# FOR EVERY CLASS NAME C AND EVERY CLASS NAME D SUCH THAT C != D WE COMPUTE S
print("########-X IN C X IN D-########")
s = {};
for c in classes:
	for d in classes:
		if(c != d):
			nb_x_in_class_query = "SELECT (COUNT(DISTINCT ?x) AS ?m) WHERE { ?x a %s . ?x a %s . }" % ("<" + c + ">", "<" + d + ">")
			s[(c, d)] = int(do_query(sparql, nb_x_in_class_query, JSON)["results"]["bindings"][0]["m"]["value"])
			print(s[(c, d)])

# COMPUTING THE BINOMIAL PROPORTION FOR EVERY CLASS
print("########-BINOMIAL PROPORTION-########")
p = {}
for (c, d) in s:
	p[(c, d)] = binomial_proportion(m[c], s[(c, d)])
	print(p[(c, d)])

# COMPUTING AVG OF EXTREMES
p_prime = {}
print("########-AVG OF EXTREMES-########")
for (c, d) in p:
	p_prime[(c, d)] = avg_of_extremes(p[(c, d)], Z, m[c])
	#p_prime[(c, d)] = p[(c, d)] + (Z * math.sqrt((p[(c, d)] * (1 - p[(c, d)])) / (m[c])))
	print(p_prime[(c, d)])

# RE-COMPUTING THE BINOMIAL PROPORTION FOR EVERY CLASS
print("########-BINOMIAL PROPORTION-########")
_p = {}
for (c, d) in s:
        _p[(c, d)] = binomial_proportion(m[c], s[(c, d)], 1)
        print(_p[(c, d)])

# COMPUTING AVG OF EXTREMES USING IMPROVED WALD INTERVAL
p_second = {}
print("########-AVG OF EXTREMES-########")
for (c, d) in _p:
        p_second[(c, d)] = avg_of_extremes(_p[(c, d)], Z, m[c] + 4)
        print(p_second[(c, d)])
