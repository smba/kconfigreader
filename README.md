kconfigreader
===========

tooling to read kconfig files and convert them into 
formulas for further reasoning (primarily for the
TypeChef infrastructure, but may be used elsewhere).

Build with `sbt`


To extract the raw data from kconfig files, this tool
relies on a patched version of undertaker's dumpconf tool
available here: https://github.com/ckaestne/undertaker
(build with `make scripts/kconfig/dumpconf`)


Instrunctions
=====


With `sbt mkrun` you can create a `run.sh` file that configures
all dependencies correctly.

To extract information from a model run `./run.sh de.fosd.typechef.kconfig.KConfigReader [kconfig] [out]`
where `kconfig` refers to the kconfig file that should be analyzed and `out` points to the base name of the
files that should be written (the tool will create multiple output files with
different extensions).

By default, the tool will create two files: `out.rsf` contains the output of undertaker-dumpconf, a raw
dump of the kconfig information in a intermediate format and `out.model` contains the boolean constraints
sorted by the feature they belong to.

The feature names in this file have the following encoding: Feature names in quotes occur undefined
in the kconfig model and are hence dead. A tristate feature X is represented by two variables X and
X_MODULE that are mutually exclusive, just as used in Linux. Nonboolean options are represented by
multiple variables, one for each value explicitly mentioned in the kconfig files (X=n means the variable
is deactived, X=1 means it has value 1, and so on).

Additional options:

  * `--dumpconf [file]` provide the path to the dumpconf tool to be called from within
    this tool

  * `--writeDimacs` writes a `out.dimacs` file that can be used with any SAT solver or
    directly as TypeChef feature model (e.g. through `FeatureExprFactory.dflt.featureModelFactory.createFromDimacsFile`).
    Comments in the beginning of the dimacs file provide a mapping to the option names (including variables
    for nonboolean options).
    The dimacs file contains additional variables to avoid explosion of the transformation into CNF
    (the transformation is equisatisfiable, but not equivalent; and equivalent transformation into CNF
    is possible for small models, but not for the larger constraints in Linux; changes are easily possible
    in the source code by changing the parameter to `DimacsWriter.writeAsDimacs2`).

  * `--writeCompletedConf` writes `out.completed.h` and `out.open` files. It checks for every option
    whether it can be activated. If it is activated in all configurations, it is defined as macro in
    the .h file, if it is deactivated in all configurations, it is undefined in the .h file. If it is
    activated in some and deactivated in other valid configurations, it is included in the .open file.
    Those files are used as input for TypeChef to reduce the search space (using TypeChef's `--include`
    and `--openFeat` parameters). Since it requires two SAT calls for every option, it is expensive to compute.
    It requires to write a .dimacs file for reasonable performance.


   * `--writeNonBoolean` writes a `out.nonbool.h` file that defines all nonboolean options to
     their defaults using #define directives. Additionally, #ifdef directives are used if
     different defaults are defined in different configurations or defaults are not available
     for all configurations.

   * `--reduceConstraints` eliminates all redundant constraints (i.e., constraints that are
     implied already by previous constraints) before writing the .dimacs file. This is a very expensive
     operation, that however can reduce the size of the .dimacs file by a few percent.




For an example of how to use this, see `genFMs.sh` in https://github.com/ckaestne/TypeChef-LinuxAnalysis


Comments and Limitations
=====

Tristate and boolean options (with prompts and without) are accurately handled as far
as we know. If you find a mistake, please provide a small kconfig file as test case
where our extraction differs from the default kconfig behavior (the test infrastructure
tests all combinations of those files in a brute-force fashion, there are many examples
of such files in the test directory).

Select statements (and depends) are potentially order dependent and may trigger kconfig to produce
otherwise invalid configurations. Kconfig issues a warning when this happens and it is rather unlikely.
Our tool does not model this extreme behavior correctly. It would be worth writing an extension
which detects potential issues to report them for to the Linux maintainers (as they try to avoid these
cases as well).

The precise handling of tristate and nonprompt options often lead to large constraints. This is
unavoidable unless imprecise approximations are desired. (Those could be added on top of our
infrastructure easily).

A different behavior for nonboolean options would be possible. Here a finite abstraction of
an infinite domain is necessary. The current encoding represents precisely what is enforced
within kconfig, but limited to the values mentioned in the kconfig file as defaults or
in constraints. A different behavior would be possibly by changing the implementation.

Range expressions currently may not depend on other configuration values, but only on constants.
This is likely sufficient for Linux.

We currently create constraints for each option separately. Select statements are listed under the
selected statement, not the selecting statement. It would be an straightforward extension to additionally distinguish
the kind of constraints further and maintain traceability information back to the .rsf file, if desired.