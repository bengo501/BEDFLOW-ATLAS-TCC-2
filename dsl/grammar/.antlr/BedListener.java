// Generated from c:\Users\joxto\Downloads\BEDFLOW-ATLAS\dsl\grammar\Bed.g4 by ANTLR 4.9.2
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link BedParser}.
 */
public interface BedListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link BedParser#bedFile}.
	 * @param ctx the parse tree
	 */
	void enterBedFile(BedParser.BedFileContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#bedFile}.
	 * @param ctx the parse tree
	 */
	void exitBedFile(BedParser.BedFileContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#section}.
	 * @param ctx the parse tree
	 */
	void enterSection(BedParser.SectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#section}.
	 * @param ctx the parse tree
	 */
	void exitSection(BedParser.SectionContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#bedSection}.
	 * @param ctx the parse tree
	 */
	void enterBedSection(BedParser.BedSectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#bedSection}.
	 * @param ctx the parse tree
	 */
	void exitBedSection(BedParser.BedSectionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code bedDiameter}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void enterBedDiameter(BedParser.BedDiameterContext ctx);
	/**
	 * Exit a parse tree produced by the {@code bedDiameter}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void exitBedDiameter(BedParser.BedDiameterContext ctx);
	/**
	 * Enter a parse tree produced by the {@code bedHeight}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void enterBedHeight(BedParser.BedHeightContext ctx);
	/**
	 * Exit a parse tree produced by the {@code bedHeight}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void exitBedHeight(BedParser.BedHeightContext ctx);
	/**
	 * Enter a parse tree produced by the {@code bedWallThickness}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void enterBedWallThickness(BedParser.BedWallThicknessContext ctx);
	/**
	 * Exit a parse tree produced by the {@code bedWallThickness}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void exitBedWallThickness(BedParser.BedWallThicknessContext ctx);
	/**
	 * Enter a parse tree produced by the {@code bedClearance}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void enterBedClearance(BedParser.BedClearanceContext ctx);
	/**
	 * Exit a parse tree produced by the {@code bedClearance}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void exitBedClearance(BedParser.BedClearanceContext ctx);
	/**
	 * Enter a parse tree produced by the {@code bedMaterial}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void enterBedMaterial(BedParser.BedMaterialContext ctx);
	/**
	 * Exit a parse tree produced by the {@code bedMaterial}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void exitBedMaterial(BedParser.BedMaterialContext ctx);
	/**
	 * Enter a parse tree produced by the {@code bedRoughness}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void enterBedRoughness(BedParser.BedRoughnessContext ctx);
	/**
	 * Exit a parse tree produced by the {@code bedRoughness}
	 * labeled alternative in {@link BedParser#bedProperty}.
	 * @param ctx the parse tree
	 */
	void exitBedRoughness(BedParser.BedRoughnessContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#lidsSection}.
	 * @param ctx the parse tree
	 */
	void enterLidsSection(BedParser.LidsSectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#lidsSection}.
	 * @param ctx the parse tree
	 */
	void exitLidsSection(BedParser.LidsSectionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code lidsTopType}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void enterLidsTopType(BedParser.LidsTopTypeContext ctx);
	/**
	 * Exit a parse tree produced by the {@code lidsTopType}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void exitLidsTopType(BedParser.LidsTopTypeContext ctx);
	/**
	 * Enter a parse tree produced by the {@code lidsBottomType}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void enterLidsBottomType(BedParser.LidsBottomTypeContext ctx);
	/**
	 * Exit a parse tree produced by the {@code lidsBottomType}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void exitLidsBottomType(BedParser.LidsBottomTypeContext ctx);
	/**
	 * Enter a parse tree produced by the {@code lidsTopThickness}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void enterLidsTopThickness(BedParser.LidsTopThicknessContext ctx);
	/**
	 * Exit a parse tree produced by the {@code lidsTopThickness}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void exitLidsTopThickness(BedParser.LidsTopThicknessContext ctx);
	/**
	 * Enter a parse tree produced by the {@code lidsBottomThickness}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void enterLidsBottomThickness(BedParser.LidsBottomThicknessContext ctx);
	/**
	 * Exit a parse tree produced by the {@code lidsBottomThickness}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void exitLidsBottomThickness(BedParser.LidsBottomThicknessContext ctx);
	/**
	 * Enter a parse tree produced by the {@code lidsSealClearance}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void enterLidsSealClearance(BedParser.LidsSealClearanceContext ctx);
	/**
	 * Exit a parse tree produced by the {@code lidsSealClearance}
	 * labeled alternative in {@link BedParser#lidsProperty}.
	 * @param ctx the parse tree
	 */
	void exitLidsSealClearance(BedParser.LidsSealClearanceContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#lidType}.
	 * @param ctx the parse tree
	 */
	void enterLidType(BedParser.LidTypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#lidType}.
	 * @param ctx the parse tree
	 */
	void exitLidType(BedParser.LidTypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#particlesSection}.
	 * @param ctx the parse tree
	 */
	void enterParticlesSection(BedParser.ParticlesSectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#particlesSection}.
	 * @param ctx the parse tree
	 */
	void exitParticlesSection(BedParser.ParticlesSectionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesKind}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesKind(BedParser.ParticlesKindContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesKind}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesKind(BedParser.ParticlesKindContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesDiameter}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesDiameter(BedParser.ParticlesDiameterContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesDiameter}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesDiameter(BedParser.ParticlesDiameterContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesCount}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesCount(BedParser.ParticlesCountContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesCount}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesCount(BedParser.ParticlesCountContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesTargetPorosity}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesTargetPorosity(BedParser.ParticlesTargetPorosityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesTargetPorosity}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesTargetPorosity(BedParser.ParticlesTargetPorosityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesDensity}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesDensity(BedParser.ParticlesDensityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesDensity}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesDensity(BedParser.ParticlesDensityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesMass}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesMass(BedParser.ParticlesMassContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesMass}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesMass(BedParser.ParticlesMassContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesRestitution}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesRestitution(BedParser.ParticlesRestitutionContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesRestitution}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesRestitution(BedParser.ParticlesRestitutionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesFriction}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesFriction(BedParser.ParticlesFrictionContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesFriction}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesFriction(BedParser.ParticlesFrictionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesRollingFriction}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesRollingFriction(BedParser.ParticlesRollingFrictionContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesRollingFriction}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesRollingFriction(BedParser.ParticlesRollingFrictionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesLinearDamping}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesLinearDamping(BedParser.ParticlesLinearDampingContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesLinearDamping}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesLinearDamping(BedParser.ParticlesLinearDampingContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesAngularDamping}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesAngularDamping(BedParser.ParticlesAngularDampingContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesAngularDamping}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesAngularDamping(BedParser.ParticlesAngularDampingContext ctx);
	/**
	 * Enter a parse tree produced by the {@code particlesSeed}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void enterParticlesSeed(BedParser.ParticlesSeedContext ctx);
	/**
	 * Exit a parse tree produced by the {@code particlesSeed}
	 * labeled alternative in {@link BedParser#particlesProperty}.
	 * @param ctx the parse tree
	 */
	void exitParticlesSeed(BedParser.ParticlesSeedContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#particleKind}.
	 * @param ctx the parse tree
	 */
	void enterParticleKind(BedParser.ParticleKindContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#particleKind}.
	 * @param ctx the parse tree
	 */
	void exitParticleKind(BedParser.ParticleKindContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#packingSection}.
	 * @param ctx the parse tree
	 */
	void enterPackingSection(BedParser.PackingSectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#packingSection}.
	 * @param ctx the parse tree
	 */
	void exitPackingSection(BedParser.PackingSectionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingMethodProp}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingMethodProp(BedParser.PackingMethodPropContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingMethodProp}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingMethodProp(BedParser.PackingMethodPropContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingGravity}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingGravity(BedParser.PackingGravityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingGravity}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingGravity(BedParser.PackingGravityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingSubsteps}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingSubsteps(BedParser.PackingSubstepsContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingSubsteps}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingSubsteps(BedParser.PackingSubstepsContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingIterations}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingIterations(BedParser.PackingIterationsContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingIterations}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingIterations(BedParser.PackingIterationsContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingDamping}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingDamping(BedParser.PackingDampingContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingDamping}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingDamping(BedParser.PackingDampingContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingRestVelocity}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingRestVelocity(BedParser.PackingRestVelocityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingRestVelocity}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingRestVelocity(BedParser.PackingRestVelocityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingMaxTime}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingMaxTime(BedParser.PackingMaxTimeContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingMaxTime}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingMaxTime(BedParser.PackingMaxTimeContext ctx);
	/**
	 * Enter a parse tree produced by the {@code packingCollisionMargin}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void enterPackingCollisionMargin(BedParser.PackingCollisionMarginContext ctx);
	/**
	 * Exit a parse tree produced by the {@code packingCollisionMargin}
	 * labeled alternative in {@link BedParser#packingProperty}.
	 * @param ctx the parse tree
	 */
	void exitPackingCollisionMargin(BedParser.PackingCollisionMarginContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#packingMethod}.
	 * @param ctx the parse tree
	 */
	void enterPackingMethod(BedParser.PackingMethodContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#packingMethod}.
	 * @param ctx the parse tree
	 */
	void exitPackingMethod(BedParser.PackingMethodContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#exportSection}.
	 * @param ctx the parse tree
	 */
	void enterExportSection(BedParser.ExportSectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#exportSection}.
	 * @param ctx the parse tree
	 */
	void exitExportSection(BedParser.ExportSectionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportFormats}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportFormats(BedParser.ExportFormatsContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportFormats}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportFormats(BedParser.ExportFormatsContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportUnits}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportUnits(BedParser.ExportUnitsContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportUnits}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportUnits(BedParser.ExportUnitsContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportScale}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportScale(BedParser.ExportScaleContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportScale}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportScale(BedParser.ExportScaleContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportWallMode}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportWallMode(BedParser.ExportWallModeContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportWallMode}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportWallMode(BedParser.ExportWallModeContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportFluidMode}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportFluidMode(BedParser.ExportFluidModeContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportFluidMode}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportFluidMode(BedParser.ExportFluidModeContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportManifoldCheck}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportManifoldCheck(BedParser.ExportManifoldCheckContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportManifoldCheck}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportManifoldCheck(BedParser.ExportManifoldCheckContext ctx);
	/**
	 * Enter a parse tree produced by the {@code exportMergeDistance}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void enterExportMergeDistance(BedParser.ExportMergeDistanceContext ctx);
	/**
	 * Exit a parse tree produced by the {@code exportMergeDistance}
	 * labeled alternative in {@link BedParser#exportProperty}.
	 * @param ctx the parse tree
	 */
	void exitExportMergeDistance(BedParser.ExportMergeDistanceContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#formatList}.
	 * @param ctx the parse tree
	 */
	void enterFormatList(BedParser.FormatListContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#formatList}.
	 * @param ctx the parse tree
	 */
	void exitFormatList(BedParser.FormatListContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#wallMode}.
	 * @param ctx the parse tree
	 */
	void enterWallMode(BedParser.WallModeContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#wallMode}.
	 * @param ctx the parse tree
	 */
	void exitWallMode(BedParser.WallModeContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#fluidMode}.
	 * @param ctx the parse tree
	 */
	void enterFluidMode(BedParser.FluidModeContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#fluidMode}.
	 * @param ctx the parse tree
	 */
	void exitFluidMode(BedParser.FluidModeContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#cfdSection}.
	 * @param ctx the parse tree
	 */
	void enterCfdSection(BedParser.CfdSectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#cfdSection}.
	 * @param ctx the parse tree
	 */
	void exitCfdSection(BedParser.CfdSectionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdRegimeProp}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdRegimeProp(BedParser.CfdRegimePropContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdRegimeProp}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdRegimeProp(BedParser.CfdRegimePropContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdInletVelocity}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdInletVelocity(BedParser.CfdInletVelocityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdInletVelocity}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdInletVelocity(BedParser.CfdInletVelocityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdFluidDensity}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdFluidDensity(BedParser.CfdFluidDensityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdFluidDensity}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdFluidDensity(BedParser.CfdFluidDensityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdFluidViscosity}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdFluidViscosity(BedParser.CfdFluidViscosityContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdFluidViscosity}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdFluidViscosity(BedParser.CfdFluidViscosityContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdMaxIterations}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdMaxIterations(BedParser.CfdMaxIterationsContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdMaxIterations}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdMaxIterations(BedParser.CfdMaxIterationsContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdConvergenceCriteria}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdConvergenceCriteria(BedParser.CfdConvergenceCriteriaContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdConvergenceCriteria}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdConvergenceCriteria(BedParser.CfdConvergenceCriteriaContext ctx);
	/**
	 * Enter a parse tree produced by the {@code cfdWriteFields}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void enterCfdWriteFields(BedParser.CfdWriteFieldsContext ctx);
	/**
	 * Exit a parse tree produced by the {@code cfdWriteFields}
	 * labeled alternative in {@link BedParser#cfdProperty}.
	 * @param ctx the parse tree
	 */
	void exitCfdWriteFields(BedParser.CfdWriteFieldsContext ctx);
	/**
	 * Enter a parse tree produced by {@link BedParser#cfdRegime}.
	 * @param ctx the parse tree
	 */
	void enterCfdRegime(BedParser.CfdRegimeContext ctx);
	/**
	 * Exit a parse tree produced by {@link BedParser#cfdRegime}.
	 * @param ctx the parse tree
	 */
	void exitCfdRegime(BedParser.CfdRegimeContext ctx);
}