#A Little Brain ExpeRimenT (ALBERT) 

ALBERT is a simple Neural Network simulator based loosely on the characteristics of biological 
neural networks.

The *model_spec.py* file contains user defined run-time parameters, cell models, a brain model, 
training parameters and cell update functions.

ALBERT assumes that cells grow and shrink dendritic spines. Once connected, the spines synapse onto connected axons.
Synapses strengthen and weaken with usage.

ALBERT was created to reason about biological neural network development and behaviour, unconstrained 
by accepted physiological and electrical models.

ALBERT accepts simple 2D models of cells composed from axons and dendrites. The number, extent and path shapes of 
axons and dendrites are user-defined. Clones of the defined cells can then be arranged in one or more 
2D spaces (Modules). User-defined bridges may connect cell components both within, and between Modules.
In addition, user-specified functions and supporting electrical and dynamic constants may be set out 
in the *model_spec.py* file.


