"""The references of the methods the program uses: ONE list, used by the window (every tab names the methods it uses with their citations, as links; menu choices that name a published method carry
its short citation), by the manual (the reference list) and by ``er3ds references``.

Every entry has a short ``tag`` (author and year, as in the text), the full citation, and a link.  ``checked`` says that the bibliographic details and the link were looked up online while the entry
was written (title, authors, journal, DOI); an entry that is not checked was written from the literature without that look-up and has NO direct link: it gets a search link (Crossref, by title and
first author), which cannot be wrong, until a link is added.  ``er3ds references --check`` tries every link (it needs a network connection).
"""
from __future__ import annotations

import urllib.parse
from dataclasses import dataclass


@dataclass(frozen=True)
class Reference:
    key: str
    tag: str                 # "Jermyn et al. 2012": how the text refers to it
    authors: str             # "Jermyn, I. H., Kurtek, S., Klassen, E. and Srivastava, A."
    year: int
    title: str
    venue: str               # journal and numbers, book series, publisher, preprint server
    url: str = ""            # a link that was checked (DOI, publisher or author page, arXiv); "" if there is none yet
    checked: bool = False    # the details (and the link) were checked online when the entry was written

    @property
    def cite(self):
        return f"{self.authors} ({self.year}). {self.title}. {self.venue}."

    @property
    def link(self):
        """The checked link, or else a Crossref search for the title and the first author."""
        if self.url:
            return self.url
        first = self.authors.split(",")[0]
        return "https://search.crossref.org/search/works?q=" + urllib.parse.quote(f"{self.title} {first}") + "&from_ui=yes"


def _r(key, tag, authors, year, title, venue, url="", checked=False):
    return key, Reference(key, tag, authors, year, title, venue, url, checked)


REFERENCES = dict([
    # ---- the elastic shape analysis of surfaces (all checked online)
    _r("jermyn2012", "Jermyn et al. 2012", "Jermyn, I. H., Kurtek, S., Klassen, E. and Srivastava, A.", 2012,
       "Elastic shape matching of parameterized surfaces using square root normal fields", "Computer Vision - ECCV 2012, Lecture Notes in Computer Science 7576", "https://doi.org/10.1007/978-3-642-33715-4_58", True),
    _r("jermyn2017", "Jermyn et al. 2017", "Jermyn, I. H., Kurtek, S., Laga, H. and Srivastava, A.", 2017,
       "Elastic Shape Analysis of Three-Dimensional Objects", "Synthesis Lectures on Computer Vision, Springer", "https://doi.org/10.1007/978-3-031-01819-0", True),
    _r("kurtek2015", "Kurtek & Drira 2015", "Kurtek, S. and Drira, H.", 2015, "A comprehensive statistical framework for elastic shape analysis of 3D faces", "Computers & Graphics 51, 52-59, doi:10.1016/j.cag.2015.05.027 (the DOI is printed on the paper itself; the link was not checked online)"),
    _r("laga2017", "Laga et al. 2017", "Laga, H., Xie, Q., Jermyn, I. H. and Srivastava, A.", 2017,
       "Numerical inversion of SRNF maps for elastic shape analysis of genus-zero surfaces", "IEEE Transactions on Pattern Analysis and Machine Intelligence 39(12), 2451-2464", "https://doi.org/10.1109/TPAMI.2016.2647596", True),
    _r("laga2022", "Laga et al. 2022", "Laga, H., Padilla, M., Jermyn, I. H., Kurtek, S., Bennamoun, M. and Srivastava, A.", 2022,
       "4D Atlas: statistical analysis of the spatiotemporal variability in longitudinal 3D shape data", "IEEE Transactions on Pattern Analysis and Machine Intelligence 45(2), 1335-1352 (published online 2022)",
       "https://doi.org/10.1109/TPAMI.2022.3163720", True),
    _r("kurtek2013", "Kurtek et al. 2013", "Kurtek, S., Srivastava, A., Klassen, E. and Laga, H.", 2013,
       "Landmark-guided elastic shape analysis of spherically-parameterized surfaces", "Computer Graphics Forum 32(2pt4), 429-438", "https://doi.org/10.1111/cgf.12063", True),
    _r("laga2022code", "Laga 2022 (code)", "Laga, H.", 2022,
       "SphericalParameterization: spherical parameterization of genus-0 mesh surfaces (a non-official implementation of Praun and Hoppe 2003)",
       "MATLAB code, GitHub repository hamidlaga/SphericalParameterization (with S. Kurtek, E. Klassen and A. Srivastava; whose readme asks to cite Kurtek et al. 2013 and Jermyn et al. 2017 with it)",
       "https://github.com/hamidlaga/SphericalParameterization", True),
    _r("zhang2023", "Zhang et al. 2023", "Zhang, Z., Wu, Y., Xiong, D., Ibrahim, J. G., Srivastava, A. and Zhu, H.", 2023,
       "LESA: longitudinal elastic shape analysis of brain subcortical structures", "Journal of the American Statistical Association 118(541), 3-17", "https://doi.org/10.1080/01621459.2022.2102984", True),
    _r("bauer2021", "Bauer et al. 2021", "Bauer, M., Charon, N., Harms, P. and Hsieh, H.-W.", 2021,
       "A numerical framework for elastic surface matching, comparison, and interpolation", "International Journal of Computer Vision 129", "https://doi.org/10.1007/s11263-021-01476-6", True),
    _r("charon2013", "Charon and Trouve 2013", "Charon, N. and Trouv\u00e9, A.", 2013,
       "The varifold representation of nonoriented shapes for diffeomorphic registration", "SIAM Journal on Imaging Sciences 6 (2013); arXiv:1304.6108", "https://arxiv.org/abs/1304.6108", True),
    _r("karcher1977", "Karcher 1977", "Karcher, H.", 1977, "Riemannian center of mass and mollifier smoothing", "Communications on Pure and Applied Mathematics 30(5), 509-541"),
    _r("fletcher2004", "Fletcher et al. 2004", "Fletcher, P. T., Lu, C., Pizer, S. M. and Joshi, S.", 2004,
       "Principal geodesic analysis for the study of nonlinear statistics of shape", "IEEE Transactions on Medical Imaging 23(8), 995-1005", "https://doi.org/10.1109/TMI.2004.831793", True),
    # ---- meshes: repair, simplification, parameterization, alignment
    _r("liepa2003", "Liepa 2003", "Liepa, P.", 2003, "Filling holes in meshes", "Eurographics Symposium on Geometry Processing, 200-205", "https://doi.org/10.2312/SGP/SGP03/200-206", True),
    _r("barequet1995", "Barequet and Sharir 1995", "Barequet, G. and Sharir, M.", 1995, "Filling gaps in the boundary of a polyhedron", "Computer Aided Geometric Design 12(2), 207-229"),
    _r("kazhdan2006", "Kazhdan et al. 2006", "Kazhdan, M., Bolitho, M. and Hoppe, H.", 2006, "Poisson surface reconstruction", "Eurographics Symposium on Geometry Processing, 61-70",
       "https://doi.org/10.2312/SGP/SGP06/061-070", True),
    _r("garland1997", "Garland and Heckbert 1997", "Garland, M. and Heckbert, P. S.", 1997, "Surface simplification using quadric error metrics", "SIGGRAPH '97, 209-216", "https://doi.org/10.1145/258734.258849", True),
    _r("praun2003", "Praun and Hoppe 2003", "Praun, E. and Hoppe, H.", 2003, "Spherical parametrization and remeshing", "ACM Transactions on Graphics (SIGGRAPH) 22(3)", "https://www.hhoppe.com/proj/sphereparam/", True),
    _r("sander2001", "Sander et al. 2001", "Sander, P. V., Snyder, J., Gortler, S. J. and Hoppe, H.", 2001, "Texture mapping progressive meshes", "SIGGRAPH 2001, 409-416"),
    _r("tutte1963", "Tutte 1963", "Tutte, W. T.", 1963, "How to draw a graph", "Proceedings of the London Mathematical Society s3-13(1), 743-767"),
    _r("floater2003", "Floater 2003", "Floater, M. S.", 2003, "Mean value coordinates", "Computer Aided Geometric Design 20(1), 19-27"),
    _r("gotsman2003", "Gotsman et al. 2003", "Gotsman, C., Gu, X. and Sheffer, A.", 2003, "Fundamentals of spherical parameterization for 3D meshes", "ACM Transactions on Graphics 22(3), 358-363", "", True),
    _r("besl1992", "Besl and McKay 1992", "Besl, P. J. and McKay, N. D.", 1992, "A method for registration of 3-D shapes", "IEEE Transactions on Pattern Analysis and Machine Intelligence 14(2), 239-256"),
    # ---- the parameterization of genus-1 surfaces (the toroidal parameterization); Yueh 2023 is taken from the bibliography of Sutti and Yueh 2025, the others were looked up online
    _r("sutti2025", "Sutti and Yueh 2025", "Sutti, M. and Yueh, M.-H.", 2025, "Toroidal area-preserving parameterizations of genus-one closed surfaces", "arXiv:2508.05111 (preprint)", "https://arxiv.org/abs/2508.05111", True),
    _r("yueh2020", "Yueh et al. 2020", "Yueh, M.-H., Li, T., Lin, W.-W. and Yau, S.-T.", 2020,
       "A new efficient algorithm for volume-preserving parameterizations of genus-one 3-manifolds", "SIAM Journal on Imaging Sciences 13(3), 1536-1564", "https://doi.org/10.1137/19M1301096", True),
    _r("yueh2023", "Yueh 2023", "Yueh, M.-H.", 2023, "Theoretical foundation of the stretch energy minimization for area-preserving simplicial mappings", "SIAM Journal on Imaging Sciences 16(3), 1142-1176",
       "https://doi.org/10.1137/22M1505062", True),
    # ---- optimization
    _r("liu1989", "Liu and Nocedal 1989", "Liu, D. C. and Nocedal, J.", 1989, "On the limited memory BFGS method for large scale optimization", "Mathematical Programming 45, 503-528"),
    _r("marquardt1963", "Marquardt 1963", "Marquardt, D. W.", 1963, "An algorithm for least-squares estimation of nonlinear parameters", "SIAM Journal on Applied Mathematics 11(2), 431-441"),
    # ---- clustering and its checks
    _r("ward1963", "Ward 1963", "Ward, J. H.", 1963, "Hierarchical grouping to optimize an objective function", "Journal of the American Statistical Association 58(301), 236-244"),
    _r("kaufman1990", "Kaufman and Rousseeuw 1990", "Kaufman, L. and Rousseeuw, P. J.", 1990, "Finding Groups in Data: An Introduction to Cluster Analysis", "Wiley"),
    _r("ng2002", "Ng et al. 2002", "Ng, A. Y., Jordan, M. I. and Weiss, Y.", 2002, "On spectral clustering: analysis and an algorithm", "Advances in Neural Information Processing Systems 14, 849-856"),
    _r("lloyd1982", "Lloyd 1982", "Lloyd, S. P.", 1982, "Least squares quantization in PCM", "IEEE Transactions on Information Theory 28(2), 129-137"),
    _r("arthur2007", "Arthur and Vassilvitskii 2007", "Arthur, D. and Vassilvitskii, S.", 2007, "k-means++: the advantages of careful seeding", "Proceedings of the 18th ACM-SIAM Symposium on Discrete Algorithms, 1027-1035"),
    _r("dempster1977", "Dempster et al. 1977", "Dempster, A. P., Laird, N. M. and Rubin, D. B.", 1977, "Maximum likelihood from incomplete data via the EM algorithm", "Journal of the Royal Statistical Society B 39(1), 1-38"),
    _r("schwarz1978", "Schwarz 1978", "Schwarz, G.", 1978, "Estimating the dimension of a model", "Annals of Statistics 6(2), 461-464"),
    _r("zhang2015", "Zhang, Pati and Srivastava 2015", "Zhang, Z., Pati, D. and Srivastava, A.", 2015, "Bayesian clustering of shapes of curves", "arXiv:1504.00377 (preprint)", "https://arxiv.org/abs/1504.00377", True),
    _r("aldous1985", "Aldous 1985", "Aldous, D. J.", 1985, "Exchangeability and related topics", "Ecole d'Ete de Probabilites de Saint-Flour XIII, Lecture Notes in Mathematics 1117, 1-198, Springer"),
    _r("geman1984", "Geman and Geman 1984", "Geman, S. and Geman, D.", 1984, "Stochastic relaxation, Gibbs distributions, and the Bayesian restoration of images", "IEEE Transactions on Pattern Analysis and Machine Intelligence 6(6), 721-741"),
    _r("deng2022", "Deng et al. 2022a", "Deng, X., Sarkar, R., Labruyere, E., Olivo-Marin, J.-C. and Srivastava, A.", 2022, "Characterizing cell populations using statistical shape modes",
       "2022 IEEE 19th International Symposium on Biomedical Imaging (ISBI)", "https://doi.org/10.1109/ISBI52829.2022.9761679", True),
    _r("deng2022b", "Deng et al. 2022b", "Deng, X., Srivastava, A., Sarkar, R., Labruyere, E. and Olivo-Marin, J.-C.", 2022, "Characterizing cell shape distributions using k-mode kernel mixtures",
       "2022 26th International Conference on Pattern Recognition (ICPR)", "https://doi.org/10.1109/ICPR56361.2022.9956604", True),
    _r("bhadra2024", "Bhadra and Srivastava 2024", "Bhadra, S. and Srivastava, A.", 2024, "Scalar-on-shape regression models for functional data analysis", "arXiv:2411.15326 [stat.ME] (preprint)",
       "https://arxiv.org/abs/2411.15326", True),
    _r("rousseeuw1987", "Rousseeuw 1987", "Rousseeuw, P. J.", 1987, "Silhouettes: a graphical aid to the interpretation and validation of cluster analysis", "Journal of Computational and Applied Mathematics 20, 53-65"),
    _r("hubert1985", "Hubert and Arabie 1985", "Hubert, L. and Arabie, P.", 1985, "Comparing partitions", "Journal of Classification 2, 193-218"),
    _r("rand1971", "Rand 1971", "Rand, W. M.", 1971, "Objective criteria for the evaluation of clustering methods", "Journal of the American Statistical Association 66(336), 846-850"),
    _r("strehl2002", "Strehl and Ghosh 2002", "Strehl, A. and Ghosh, J.", 2002, "Cluster ensembles - a knowledge reuse framework for combining multiple partitions", "Journal of Machine Learning Research 3, 583-617"),
    _r("iglewicz1993", "Iglewicz and Hoaglin 1993", "Iglewicz, B. and Hoaglin, D. C.", 1993, "How to Detect and Handle Outliers", "ASQC Quality Press"),
    _r("hampel1974", "Hampel 1974", "Hampel, F. R.", 1974, "The influence curve and its role in robust estimation", "Journal of the American Statistical Association 69(346), 383-393"),
    # ---- regression and trajectories
    _r("yao2005", "Yao, Mueller and Wang 2005", "Yao, F., M\u00fcller, H.-G. and Wang, J.-L.", 2005, "Functional data analysis for sparse longitudinal data", "Journal of the American Statistical Association 100(470), 577-590",
       "https://doi.org/10.1198/016214504000001745", True),
    _r("laird1982", "Laird and Ware 1982", "Laird, N. M. and Ware, J. H.", 1982, "Random-effects models for longitudinal data", "Biometrics 38(4), 963-974"),
    _r("patterson1971", "Patterson and Thompson 1971", "Patterson, H. D. and Thompson, R.", 1971, "Recovery of inter-block information when block sizes are unequal", "Biometrika 58(3), 545-554"),
    _r("eilers1996", "Eilers and Marx 1996", "Eilers, P. H. C. and Marx, B. D.", 1996, "Flexible smoothing with B-splines and penalties", "Statistical Science 11(2), 89-121"),
    _r("ruppert2003", "Ruppert et al. 2003", "Ruppert, D., Wand, M. P. and Carroll, R. J.", 2003, "Semiparametric Regression", "Cambridge University Press"),
    _r("fan1996", "Fan and Gijbels 1996", "Fan, J. and Gijbels, I.", 1996, "Local Polynomial Modelling and Its Applications", "Chapman and Hall"),
    _r("akaike1974", "Akaike 1974", "Akaike, H.", 1974, "A new look at the statistical model identification", "IEEE Transactions on Automatic Control 19(6), 716-723"),
    _r("stone1974", "Stone 1974", "Stone, M.", 1974, "Cross-validatory choice and assessment of statistical predictions", "Journal of the Royal Statistical Society B 36(2), 111-147"),
    _r("efron1979", "Efron 1979", "Efron, B.", 1979, "Bootstrap methods: another look at the jackknife", "Annals of Statistics 7(1), 1-26"),
    _r("freedman1983", "Freedman and Lane 1983", "Freedman, D. and Lane, D.", 1983, "A nonstochastic interpretation of reported significance levels", "Journal of Business and Economic Statistics 1(4), 292-298"),
    _r("hoerl1970", "Hoerl and Kennard 1970", "Hoerl, A. E. and Kennard, R. W.", 1970, "Ridge regression: biased estimation for nonorthogonal problems", "Technometrics 12(1), 55-67"),
    _r("nelder1972", "Nelder and Wedderburn 1972", "Nelder, J. A. and Wedderburn, R. W. M.", 1972, "Generalized linear models", "Journal of the Royal Statistical Society A 135(3), 370-384"),
])


# The methods every tab uses, with their references: (what it is used for, (keys)).  The key of a tab is the one of the window; "0" and "1" are the genus of the surfaces.
TAB_REFS = {  # (the Registration tab of genus-1 surfaces, "reg1", names no references yet: it is left out on purpose)
    "pre0": [("Closing holes", ("liepa2003", "barequet1995")), ("Poisson reconstruction", ("kazhdan2006",)), ("Mesh simplification", ("garland1997",))],
    "pre1": [("Closing holes", ("liepa2003", "barequet1995")), ("Mesh simplification", ("garland1997",))],
    "param1": [("Toroidal parameterization", ("sutti2025", "yueh2020", "yueh2023"))],
    "new1": [("Toroidal parameterization", ("sutti2025", "yueh2020", "yueh2023"))],
    "geo1": [("Geodesics in SRNF space", ("jermyn2012", "jermyn2017")), ("SRNF inversion", ("laga2017",))],
    "param0": [("Spherical parameterization", ("praun2003", "laga2022code", "kurtek2013", "jermyn2017", "sander2001")), ("Tutte embedding", ("tutte1963", "floater2003", "gotsman2003")), ("Initial alignment", ("besl1992",))],
    "reg0": [("Elastic registration, SRNF", ("jermyn2012", "jermyn2017", "laga2022")), ("SRNF inversion", ("laga2017",)), ("Solvers", ("marquardt1963", "liu1989")), ("Karcher mean", ("karcher1977",))],
    "varifold": [("Elastic-varifold matching", ("bauer2021", "charon2013")), ("Karcher mean and SRNF inversion", ("karcher1977", "jermyn2012", "laga2017"))],
    "new0": [("Elastic registration to a mean, SRNF", ("jermyn2012", "jermyn2017", "laga2017")), ("Parameterization", ("praun2003", "laga2022code")), ("Initial alignment", ("besl1992",))],
    "pre2": [("Closing holes", ("liepa2003", "barequet1995"))],
    "pre3": [("Closing holes", ("liepa2003", "barequet1995")), ("Mesh simplification", ("garland1997",))],
    "new3": [("Elastic-varifold matching", ("bauer2021", "charon2013")), ("Karcher mean and SRNF inversion", ("karcher1977", "jermyn2012", "laga2017"))],
    "geo3": [("Geodesics in SRNF space", ("jermyn2012", "jermyn2017")), ("SRNF inversion", ("laga2017",))],
    "param2": [("Elastic framework for hemispherical (disk) surfaces", ("kurtek2015", "jermyn2012", "jermyn2017")), ("Mean-value parameterization onto the disk", ("floater2003",)), ("Initial alignment", ("besl1992",))],
    "reg2": [("Elastic SRNF registration of disk surfaces", ("kurtek2015", "jermyn2012", "jermyn2017")), ("Solvers", ("marquardt1963",)), ("Karcher mean", ("karcher1977",))],
    "geo0": [("Geodesics in SRNF space", ("jermyn2012", "jermyn2017")), ("SRNF inversion", ("laga2017",))],
    "pca": [("Tangent PCA at the Karcher mean", ("fletcher2004", "jermyn2017", "karcher1977")), ("PCA in shape space, as in LESA", ("zhang2023",))],
    "cluster": [("Elastic distance", ("jermyn2017",)), ("Hierarchical", ("ward1963", "jermyn2017")), ("k-medoids", ("kaufman1990",)), ("Spectral", ("ng2002",)), ("k-means", ("lloyd1982", "arthur2007")),
                ("Mixture, BIC", ("dempster1977", "schwarz1978")), ("Bayesian", ("zhang2015", "aldous1985", "geman1984")), ("Mode-based", ("deng2022", "deng2022b")), ("Number of clusters", ("rousseeuw1987",)),
                ("Agreement with classes", ("hubert1985", "rand1971", "strehl2002")), ("Outliers", ("iglewicz1993", "hampel1974"))],
    "regress": [("Permutation tests", ("freedman1983",)), ("Logistic regression", ("nelder1972",)), ("Ridge regression", ("hoerl1970",)), ("Cross-validation", ("stone1974",)), ("Bootstrap", ("efron1979",)), ("Shape models with a regression phase and an index function", ("bhadra2024",))],
    "times": [("Longitudinal elastic shape analysis", ("zhang2023",)), ("PACE", ("yao2005",)), ("Mixed-effects model", ("laird1982", "patterson1971")), ("Local linear smoother", ("fan1996",)),
              ("Penalized splines", ("eilers1996", "ruppert2003")), ("Model choice", ("akaike1974",)), ("Bootstrap", ("efron1979",))],
    "video": [("Principal deformations and geodesics", ("jermyn2017",))],
}


TOPIC_TITLES = {"pre0": "Preprocessing (genus 0)", "pre1": "Preprocessing (genus 1)", "param0": "Parameterization (genus 0)", "param1": "Parameterization (genus 1)", "pre2": "Preprocessing (disk surfaces)", "pre3": "Preprocessing (any surface)", "new3": "Register New Shapes (any surface, elastic-varifold)", "geo3": "Geodesics (any surface)", "param2": "Parameterization (disk surfaces)", "reg2": "Registration (disk surfaces)", "reg0": "Registration (genus 0)",
                "varifold": "Registration, elastic-varifold method", "new0": "Register New Shapes (genus 0)", "new1": "Register New Shapes (genus 1: the parameterization)", "geo0": "Geodesics (genus 0)",
                "geo1": "Geodesics (genus 1)", "pca": "PCA", "cluster": "Shape Clustering", "regress": "Shape Regression", "times": "Time Models", "video": "Videos/GIFS/Images"}


def reference(key):
    return REFERENCES[key]


def tag(key):
    return REFERENCES[key].tag


def cite(*keys):
    """The short citation for a menu choice: ``(Ward 1963)`` or ``(Lloyd 1982; Arthur and Vassilvitskii 2007)``."""
    return "(" + "; ".join(REFERENCES[k].tag for k in keys) + ")"


def tab_references(topic):
    """``[(what, [Reference, ...]), ...]`` of a tab (empty if it uses no published method)."""
    return [(what, [REFERENCES[k] for k in keys]) for what, keys in TAB_REFS.get(topic, [])]


def used_by():
    """``{key: [tab topics that name it]}``."""
    out = {}
    for topic, groups in TAB_REFS.items():
        for _, keys in groups:
            for k in keys:
                out.setdefault(k, [])
                if topic not in out[k]:
                    out[k].append(topic)
    return out


def latex(text):
    """A text for LaTeX (the few special characters the references have)."""
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "_": r"\_", "#": r"\#", "\u00fc": r"\"u", "\u00e9": r"\'e", "~": r"\textasciitilde{}"}
    return "".join(rep.get(c, c) for c in text)


def bibliography_latex():
    """The reference list of the manual: every reference, alphabetically by tag, with its link."""
    items = []
    for key, r in sorted(REFERENCES.items(), key=lambda kv: kv[1].tag.lower()):
        href = r"\href{" + r.link.replace("%", r"\%").replace("#", r"\#") + "}{" + ("link" if r.url else "search") + "}"
        items.append(r"\item[\textbf{" + latex(r.tag) + r"}] " + latex(r.cite) + " " + href + ".")
    return "\\begin{description}[leftmargin=1.2cm,style=nextline,itemsep=2pt]\n" + "\n".join(items) + "\n\\end{description}\n"


def markdown():
    """The reference list of the README (between the markers of the README; a test keeps the two equal)."""
    used = used_by()
    lines = []
    for r in sorted(REFERENCES.values(), key=lambda r: r.tag.lower()):
        where = ", ".join(TOPIC_TITLES[t] for t in used.get(r.key, []))
        lines.append(f"* **{r.tag}**: {r.cite} [{'link' if r.url else 'search'}]({r.link})" + (f"  (used in: {where})" if where else ""))
    return "\n".join(lines) + "\n"
