from __future__ import print_function
import doctest, inspect, os, sys, getopt, collections
import snappy
import snappy.snap.test
import spherogram.test
import snappy.verify.test
import snappy.ptolemy.test
import snappy.raytracing.cohomology_fractal
import snappy.raytracing.geodesic
import snappy.raytracing.geodesics
import snappy.raytracing.ideal_raytracing_data
import snappy.raytracing.upper_halfspace_utilities

from snappy.sage_helper import (_within_sage, doctest_modules, cyopengl_works,
                                tk_root, root_is_fake, DocTestParser)
from snappy import numeric_output_checker
modules = []

snappy.database.Manifold = snappy.SnapPy.Manifold
# To make the floating point tests work on different platforms/compilers
snappy.number.Number._accuracy_for_testing = 8

def use_snappy_field_conversion():
    snappy.Manifold.use_field_conversion('snappy')
    snappy.ManifoldHP.use_field_conversion('snappy')

def use_sage_field_conversion():
    import sage.all
    snappy.Manifold.use_field_conversion('sage')
    snappy.ManifoldHP.use_field_conversion('sage')

# If in Sage, undo some output conversions to make the docstrings work:
if _within_sage:
    use_snappy_field_conversion()

# Augment tests for SnapPy with those that Cython missed

missed_classes =   ['Triangulation', 'Manifold',
  'AbelianGroup', 'FundamentalGroup', 'HolonomyGroup',
  'DirichletDomain', 'CuspNeighborhood', 'SymmetryGroup',
  'AlternatingKnotExteriors', 'NonalternatingKnotExteriors']

for A in missed_classes:
    snappy.SnapPy.__test__[A + '_extra'] = getattr(snappy, A).__doc__
    snappy.SnapPyHP.__test__[A + '_extra'] = getattr(snappy, A).__doc__

# some things we don't want to test at the extension module level
identify_tests = [x for x in snappy.SnapPyHP.__test__
                  if x.startswith('Manifold.identify')]
triangulation_tests = [x for x in snappy.SnapPyHP.__test__
                  if x.startswith('get_triangulation_tester')]
browser_tests = [x for x in snappy.SnapPyHP.__test__
                 if x.startswith('Manifold.browse')]
for key in identify_tests + triangulation_tests + browser_tests:
    snappy.SnapPyHP.__test__.pop(key)

if _within_sage:
    def snap_doctester(verbose):
        use_sage_field_conversion()
        ans = snappy.snap.test.run_doctests(verbose, print_info=False)
        use_snappy_field_conversion()
        return ans
else:
    def snap_doctester(verbose):
        return snappy.snap.test.run_doctests(verbose, print_info=False)

snap_doctester.__name__ = 'snappy.snap'

if _within_sage:
    def snappy_doctester(verbose):
        use_sage_field_conversion()
        ans = doctest_modules([snappy], verbose)
        use_snappy_field_conversion()
        return ans
else:
    def snappy_doctester(verbose):
        original_accuracy = snappy.number.Number._accuracy_for_testing
        snappy.number.Number._accuracy_for_testing = None
        ans = doctest_modules([snappy], verbose)
        snappy.number.Number._accuracy_for_testing = original_accuracy
        return ans

snappy_doctester.__name__ = 'snappy'

raytracing_modules = [
    snappy.raytracing.cohomology_fractal,
    snappy.raytracing.geodesic,
    snappy.raytracing.geodesics,
    snappy.raytracing.ideal_raytracing_data,
    snappy.raytracing.upper_halfspace_utilities
]

if _within_sage:
    def raytracing_doctester(verbose):
        use_sage_field_conversion()
        ans = doctest_modules(raytracing_modules, verbose)
        use_snappy_field_conversion()
        return ans
else:
    def raytracing_doctester(verbose):
        ans = doctest_modules(raytracing_modules, verbose)
        return ans

raytracing_doctester.__name__ = 'snappy.raytracing'

def spherogram_doctester(verbose):
    return spherogram.test.run_doctests(verbose, print_info=False)
spherogram_doctester.__name__ = 'spherogram'

def ptolemy_doctester(verbose):
    return snappy.ptolemy.test.run_doctests(verbose, print_info=False)
ptolemy_doctester.__name__ = 'snappy.ptolemy'

modules += [numeric_output_checker.run_doctests]

if not _within_sage:
    def number_doctester(verbose):
        original_accuracy = snappy.number.Number._accuracy_for_testing
        snappy.number.Number._accuracy_for_testing = None
        ans = doctest_modules([snappy.number], verbose)
        snappy.number.Number._accuracy_for_testing = original_accuracy
        return ans
    modules += [number_doctester]

modules += [snappy.SnapPy, snappy.SnapPyHP, snappy.database,
            snappy_doctester,
            snap_doctester,
            raytracing_doctester,
            ptolemy_doctester, spherogram_doctester]

if _within_sage:
    def snappy_verify_doctester(verbose):
        use_sage_field_conversion()
        ans = snappy.verify.test.run_doctests(verbose, print_info=False)
        use_snappy_field_conversion()
        return ans
else:
    def snappy_verify_doctester(verbose):
        old_accuracy = snappy.number.Number._accuracy_for_testing
        snappy.number.Number._accuracy_for_testing = None
        ans = snappy.verify.test.run_doctests(verbose, print_info=False)
        snappy.number.Number._accuracy_for_testing = old_accuracy
        return ans

snappy_verify_doctester.__name__ = 'snappy.verify'
modules.append(snappy_verify_doctester)

def graphics_failures(verbose, windows, use_modernopengl):
    if _within_sage:
        use_sage_field_conversion()
    if cyopengl_works():
        print("Testing graphics ...")
        import snappy.CyOpenGL
        result = doctest_modules([snappy.CyOpenGL], verbose=verbose).failed
        snappy.Manifold('m004').dirichlet_domain().view().test()
        snappy.Manifold('m125').cusp_neighborhood().view().test()
        if use_modernopengl:
            snappy.Manifold('m004').inside_view().test()
        snappy.Manifold('4_1').browse().test()
        snappy.ManifoldHP('m004').dirichlet_domain().view().test()
        snappy.ManifoldHP('m125').cusp_neighborhood().view().test()
        if use_modernopengl:
            snappy.ManifoldHP('m004').inside_view().test()
        if root_is_fake():
            root = tk_root()
            if root:
                if windows:
                    print('Close the root window to finish.')
                else:
                    print('The windows will close in a few seconds.\n'
                        'Specify -w or --windows to avoid this.')
                    root.after(7000, root.destroy)
                root.mainloop()
    else:
        print("***Warning***: CyOpenGL not installed, so not tested")
        result = 0
    if _within_sage:
        use_snappy_field_conversion()
    return result

def runtests(verbose = False,
             quick = False,
             windows = False,
             use_modernopengl = True):

    DocTestParser.use_modernopengl = use_modernopengl
    
    result = doctest_modules(modules, verbose=verbose)
    if not quick:
        print()
        # No idea why we mess and set snappy.database.Manifold
        # to SnapPy.Manifold above... But to make ptolemy work,
        # temporarily setting it to what it should be.
        original_db_manifold = snappy.database.Manifold
        snappy.database.Manifold = snappy.Manifold
        snappy.ptolemy.test.main(verbose=verbose, doctest=False)
        snappy.database.Manifold = original_db_manifold
        print()
        spherogram.links.test.run()
    print('\nAll doctests:\n   %s failures out of %s tests.' % result)

    num_graphics_failures =  graphics_failures(
        verbose=verbose,
        windows = windows,
        use_modernopengl = use_modernopengl) 
    
    return result.failed + num_graphics_failures

if __name__ == '__main__':

    verbose = False
    quick = False
    windows = False
    use_modernopengl = True
    
    try:
        useful_args = [arg for arg in sys.argv[1:] if not arg.startswith('-psn_')]
        optlist, args = getopt.getopt(
            useful_args,
            'ivqws',
            ['ignore', 'verbose', 'quick', 'windows', 'skip-modern-opengl'])
        opts = [o[0] for o in optlist]
        if '-v' in opts or '--verbose' in opts:
            verbose = True
        if '-q' in opts or '--quick' in opts:
            quick = True
        if '-w' in opts or '--windows' in opts:
            windows = True
        if '-s' in opts or '--skip-modern-opengl' in opts:
            use_modernopengl = False

    except getopt.GetoptError:
        print("Could not parse arguments")

    sys.exit(runtests(verbose = verbose,
                      quick = quick,
                      windows = windows,
                      use_modernopengl = use_modernopengl))
