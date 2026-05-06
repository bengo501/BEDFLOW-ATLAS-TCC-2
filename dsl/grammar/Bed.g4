// gramatica para arquivos .bed
grammar Bed;

// regra principal: um arquivo .bed
bedFile: section+ EOF;

// secoes principais do arquivo .bed
section: bedSection 
       | lidsSection 
       | particlesSection 
       | packingSection 
       | exportSection 
       | cfdSection;

// secao bed: define geometria do leito cilindrico
bedSection: 'bed' '{' bedProperty+ '}';
bedProperty: 'diameter' '=' NUMBER UNIT ';'         # bedDiameter
           | 'height' '=' NUMBER UNIT ';'           # bedHeight  
           | 'wall_thickness' '=' NUMBER UNIT ';'   # bedWallThickness
           | 'clearance' '=' NUMBER UNIT ';'        # bedClearance
           | 'material' '=' STRING ';'              # bedMaterial
           | 'roughness' '=' NUMBER UNIT ';'        # bedRoughness;

// secao lids: define tampas superior e inferior
lidsSection: 'lids' '{' lidsProperty+ '}';
lidsProperty: 'top_type' '=' lidType ';'            # lidsTopType
            | 'bottom_type' '=' lidType ';'         # lidsBottomType
            | 'top_thickness' '=' NUMBER UNIT ';'   # lidsTopThickness
            | 'bottom_thickness' '=' NUMBER UNIT ';' # lidsBottomThickness
            | 'seal_clearance' '=' NUMBER UNIT ';'  # lidsSealClearance;

lidType: 'flat' | 'hemispherical' | 'none' | STRING;

// secao particles: define particulas e suas propriedades
particlesSection: 'particles' '{' particlesProperty+ '}';
particlesProperty: 'kind' '=' particleKind ';'          # particlesKind
                 | 'diameter' '=' NUMBER UNIT ';'       # particlesDiameter
                 | 'count' '=' NUMBER ';'               # particlesCount
                 | 'target_porosity' '=' NUMBER ';'     # particlesTargetPorosity
                 | 'density' '=' NUMBER UNIT ';'        # particlesDensity
                 | 'mass' '=' NUMBER UNIT ';'           # particlesMass
                 | 'restitution' '=' NUMBER ';'         # particlesRestitution
                 | 'friction' '=' NUMBER ';'            # particlesFriction
                 | 'rolling_friction' '=' NUMBER ';'    # particlesRollingFriction
                 | 'linear_damping' '=' NUMBER ';'      # particlesLinearDamping
                 | 'angular_damping' '=' NUMBER ';'     # particlesAngularDamping
                 | 'seed' '=' NUMBER ';'                # particlesSeed;

particleKind: 'sphere' | 'cube' | 'cylinder' | STRING;

// secao packing: controle do empacotamento fisico
packingSection: 'packing' '{' packingProperty+ '}';
packingProperty: 'method' '=' packingMethod ';'        # packingMethodProp
               | 'gravity' '=' NUMBER UNIT ';'         # packingGravity
               | 'substeps' '=' NUMBER ';'             # packingSubsteps
               | 'iterations' '=' NUMBER ';'           # packingIterations
               | 'damping' '=' NUMBER ';'              # packingDamping
               | 'rest_velocity' '=' NUMBER UNIT ';'   # packingRestVelocity
               | 'max_time' '=' NUMBER UNIT ';'        # packingMaxTime
               | 'collision_margin' '=' NUMBER UNIT ';' # packingCollisionMargin;

packingMethod: 'rigid_body' | STRING;

// secao export: configuracao de exportacao
exportSection: 'export' '{' exportProperty+ '}';
exportProperty: 'formats' '=' '[' formatList ']' ';'   # exportFormats
              | 'units' '=' STRING ';'                 # exportUnits
              | 'scale' '=' NUMBER ';'                 # exportScale
              | 'wall_mode' '=' wallMode ';'           # exportWallMode
              | 'fluid_mode' '=' fluidMode ';'         # exportFluidMode
              | 'manifold_check' '=' BOOLEAN ';'       # exportManifoldCheck
              | 'merge_distance' '=' NUMBER UNIT ';'   # exportMergeDistance;

formatList: STRING (',' STRING)*; // lista de formatos de saida
wallMode: 'surface' | 'solid' | STRING; // superfice ou solido
fluidMode: 'none' | 'cavity' | STRING; // sem cavidade ou com cavidade

// secao cfd: parametros opcionais para CFD
cfdSection: 'cfd' '{' cfdProperty+ '}'; // secao cfd
cfdProperty: 'regime' '=' cfdRegime ';'                # cfdRegimeProp // regime laminar ou turbulento
           | 'inlet_velocity' '=' NUMBER UNIT ';'      # cfdInletVelocity // velocidade de entrada
           | 'fluid_density' '=' NUMBER UNIT ';'       # cfdFluidDensity // densidade do fluido
           | 'fluid_viscosity' '=' NUMBER UNIT ';'     # cfdFluidViscosity // viscosidade do fluido
           | 'max_iterations' '=' NUMBER ';'           # cfdMaxIterations // iteracoes maximas
           | 'convergence_criteria' '=' NUMBER ';'     # cfdConvergenceCriteria // criterio de convergencia
           | 'write_fields' '=' BOOLEAN ';'            # cfdWriteFields; // escrever campos

cfdRegime: 'laminar' | 'turbulent_rans' | STRING; // regime laminar ou turbulento

// tokens lexicos: numeros, unidades, strings e booleanos
// notacao cientifica opcional ex 1.8e-5 1e-6
NUMBER: '-'? [0-9]+ ('.' [0-9]+)? ([eE] [+-]? [0-9]+)?;
INTEGER: '-'? [0-9]+; // numeros inteiros (incluindo negativos)
UNIT: 'm' | 'cm' | 'mm' | 'kg' | 'g' | 's' | 'Pa' | 'N' | 'm/s' | 'kg/m3' | 'Pa.s' | 'm/s2' | 'm/s²'; // unidades de medida
STRING: '"' (~["\r\n])* '"'; // strings entre aspas
BOOLEAN: 'true' | 'false'; // booleanos

// ignorar espacos e comentarios
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
// comentario bloco multilinha (c-style)
BLOCK_COMMENT: '/*' ( ~'*' | '*' ~'/' )* '*/' -> skip;
