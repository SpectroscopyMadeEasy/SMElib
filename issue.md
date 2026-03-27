# SMElib Notes

## EOS default list and placeholder molecular partition functions

`H3+` should not be included in the default EOS species list.

In the current EOS implementation, enabling `H3+` in the default network can
drive the solution toward significantly larger `XNE`, `H-`, and `AHMIN`, which
in turn makes Balmer lines much too shallow for cool-star cases such as
Gmb1830.

The immediate practical workaround is to keep `H3+` out of the default EOS
list unless its thermodynamic treatment is revisited.

Related note: `MOLCON` still contains many species with placeholder-style
partition-function coefficients (for example constant `Q` behavior from
`PCOEF = 1.0, 9*0.`-type entries). These species should be audited
systematically, especially hydrogen-bearing and charged molecules that can
affect the electron balance.

## IR Brackett pseudo-continuum depression

The pseudo-continuum depression around 1.5 micron is dominated by high-order
Brackett `H 1` lines rather than by the true continuum opacity.

Tests in the current `hlinop.f` implementation indicate that the effect is
controlled almost entirely by the `STARK1` term for high-order `n -> 4`
transitions. Turning off the Stark contribution removes the depression almost
completely, while removing the self/He/radiative contribution has negligible
impact.

This looks like an old issue in the Stark treatment for high-order Brackett
lines, not a recent regression.
