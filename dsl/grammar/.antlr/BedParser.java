// Generated from c:\Users\joxto\Downloads\BEDFLOW-ATLAS\dsl\grammar\Bed.g4 by ANTLR 4.9.2
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class BedParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.9.2", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, T__8=9, 
		T__9=10, T__10=11, T__11=12, T__12=13, T__13=14, T__14=15, T__15=16, T__16=17, 
		T__17=18, T__18=19, T__19=20, T__20=21, T__21=22, T__22=23, T__23=24, 
		T__24=25, T__25=26, T__26=27, T__27=28, T__28=29, T__29=30, T__30=31, 
		T__31=32, T__32=33, T__33=34, T__34=35, T__35=36, T__36=37, T__37=38, 
		T__38=39, T__39=40, T__40=41, T__41=42, T__42=43, T__43=44, T__44=45, 
		T__45=46, T__46=47, T__47=48, T__48=49, T__49=50, T__50=51, T__51=52, 
		T__52=53, T__53=54, T__54=55, T__55=56, T__56=57, T__57=58, T__58=59, 
		T__59=60, T__60=61, T__61=62, T__62=63, T__63=64, T__64=65, T__65=66, 
		T__66=67, T__67=68, T__68=69, T__69=70, T__70=71, T__71=72, T__72=73, 
		T__73=74, T__74=75, T__75=76, T__76=77, T__77=78, T__78=79, T__79=80, 
		T__80=81, T__81=82, T__82=83, T__83=84, T__84=85, T__85=86, T__86=87, 
		T__87=88, T__88=89, T__89=90, T__90=91, T__91=92, T__92=93, T__93=94, 
		T__94=95, T__95=96, T__96=97, T__97=98, T__98=99, T__99=100, T__100=101, 
		T__101=102, T__102=103, T__103=104, T__104=105, T__105=106, T__106=107, 
		T__107=108, T__108=109, T__109=110, T__110=111, T__111=112, T__112=113, 
		T__113=114, T__114=115, T__115=116, NUMBER=117, INTEGER=118, UNIT=119, 
		STRING=120, BOOLEAN=121, WS=122, COMMENT=123, BLOCK_COMMENT=124;
	public static final int
		RULE_bedFile = 0, RULE_section = 1, RULE_bedSection = 2, RULE_bedProperty = 3, 
		RULE_visibilityProperty = 4, RULE_lidsSection = 5, RULE_lidsProperty = 6, 
		RULE_lidType = 7, RULE_particlesSection = 8, RULE_particlesProperty = 9, 
		RULE_particleKind = 10, RULE_packingSection = 11, RULE_packingProperty = 12, 
		RULE_demProperty = 13, RULE_packingMethod = 14, RULE_exportSection = 15, 
		RULE_exportProperty = 16, RULE_formatList = 17, RULE_wallMode = 18, RULE_fluidMode = 19, 
		RULE_cfdSection = 20, RULE_cfdProperty = 21, RULE_cfdRegime = 22, RULE_geometrySection = 23, 
		RULE_geometryProperty = 24, RULE_geometryMode = 25, RULE_generationSection = 26, 
		RULE_generationProperty = 27, RULE_generationBackend = 28, RULE_sliceSection = 29, 
		RULE_sliceProperty = 30, RULE_statistical2dSection = 31, RULE_statistical2dProperty = 32;
	private static String[] makeRuleNames() {
		return new String[] {
			"bedFile", "section", "bedSection", "bedProperty", "visibilityProperty", 
			"lidsSection", "lidsProperty", "lidType", "particlesSection", "particlesProperty", 
			"particleKind", "packingSection", "packingProperty", "demProperty", "packingMethod", 
			"exportSection", "exportProperty", "formatList", "wallMode", "fluidMode", 
			"cfdSection", "cfdProperty", "cfdRegime", "geometrySection", "geometryProperty", 
			"geometryMode", "generationSection", "generationProperty", "generationBackend", 
			"sliceSection", "sliceProperty", "statistical2dSection", "statistical2dProperty"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'bed'", "'{'", "'}'", "'diameter'", "'='", "';'", "'height'", 
			"'wall_thickness'", "'clearance'", "'material'", "'roughness'", "'internal_cylinder_mode'", 
			"'visibility'", "'show_outer_cylinder'", "'show_internal_cylinder'", 
			"'show_particles'", "'show_boolean_tools'", "'export_boolean_tools'", 
			"'lids'", "'top_type'", "'bottom_type'", "'top_thickness'", "'bottom_thickness'", 
			"'seal_clearance'", "'flat'", "'hemispherical'", "'none'", "'particles'", 
			"'kind'", "'count'", "'target_porosity'", "'density'", "'mass'", "'restitution'", 
			"'friction'", "'rolling_friction'", "'linear_damping'", "'angular_damping'", 
			"'seed'", "'sphere'", "'cube'", "'cylinder'", "'packing'", "'method'", 
			"'gravity'", "'substeps'", "'iterations'", "'damping'", "'rest_velocity'", 
			"'max_time'", "'collision_margin'", "'gap'", "'random_seed'", "'max_placement_attempts'", 
			"'strict_validation'", "'step_x'", "'mesh_segmentos'", "'sphere_lat'", 
			"'sphere_lon'", "'use_legacy_drop'", "'dem'", "'time_step'", "'steps'", 
			"'stiffness'", "'settle_threshold'", "'max_velocity_threshold'", "'rigid_body'", 
			"'export'", "'formats'", "'['", "']'", "'units'", "'scale'", "'wall_mode'", 
			"'fluid_mode'", "'manifold_check'", "'merge_distance'", "','", "'surface'", 
			"'solid'", "'cavity'", "'cfd'", "'regime'", "'inlet_velocity'", "'fluid_density'", 
			"'fluid_viscosity'", "'max_iterations'", "'convergence_criteria'", "'write_fields'", 
			"'laminar'", "'turbulent_rans'", "'geometry'", "'mode'", "'full_3d'", 
			"'pseudo_2d_thin_slice'", "'pseudo_2d_statistical'", "'generation'", 
			"'backend'", "'python_engine'", "'blender'", "'slice'", "'enabled'", 
			"'thickness'", "'axis'", "'position'", "'keep_only_intersecting_particles'", 
			"'preserve_original_packing'", "'slice_particle_policy'", "'debug_export_gizmos'", 
			"'min_slice_particle_radius'", "'statistical_2d'", "'domain_width'", 
			"'domain_height'", "'tolerance'", "'max_attempts'", "'slice_thickness'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, "NUMBER", "INTEGER", 
			"UNIT", "STRING", "BOOLEAN", "WS", "COMMENT", "BLOCK_COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "Bed.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public BedParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	public static class BedFileContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(BedParser.EOF, 0); }
		public List<SectionContext> section() {
			return getRuleContexts(SectionContext.class);
		}
		public SectionContext section(int i) {
			return getRuleContext(SectionContext.class,i);
		}
		public BedFileContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_bedFile; }
	}

	public final BedFileContext bedFile() throws RecognitionException {
		BedFileContext _localctx = new BedFileContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_bedFile);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(67); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(66);
				section();
				}
				}
				setState(69); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__0) | (1L << T__18) | (1L << T__27) | (1L << T__42))) != 0) || ((((_la - 68)) & ~0x3f) == 0 && ((1L << (_la - 68)) & ((1L << (T__67 - 68)) | (1L << (T__81 - 68)) | (1L << (T__91 - 68)) | (1L << (T__96 - 68)) | (1L << (T__100 - 68)) | (1L << (T__110 - 68)))) != 0) );
			setState(71);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class SectionContext extends ParserRuleContext {
		public BedSectionContext bedSection() {
			return getRuleContext(BedSectionContext.class,0);
		}
		public LidsSectionContext lidsSection() {
			return getRuleContext(LidsSectionContext.class,0);
		}
		public ParticlesSectionContext particlesSection() {
			return getRuleContext(ParticlesSectionContext.class,0);
		}
		public PackingSectionContext packingSection() {
			return getRuleContext(PackingSectionContext.class,0);
		}
		public ExportSectionContext exportSection() {
			return getRuleContext(ExportSectionContext.class,0);
		}
		public CfdSectionContext cfdSection() {
			return getRuleContext(CfdSectionContext.class,0);
		}
		public GeometrySectionContext geometrySection() {
			return getRuleContext(GeometrySectionContext.class,0);
		}
		public GenerationSectionContext generationSection() {
			return getRuleContext(GenerationSectionContext.class,0);
		}
		public SliceSectionContext sliceSection() {
			return getRuleContext(SliceSectionContext.class,0);
		}
		public Statistical2dSectionContext statistical2dSection() {
			return getRuleContext(Statistical2dSectionContext.class,0);
		}
		public SectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_section; }
	}

	public final SectionContext section() throws RecognitionException {
		SectionContext _localctx = new SectionContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_section);
		try {
			setState(83);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__0:
				enterOuterAlt(_localctx, 1);
				{
				setState(73);
				bedSection();
				}
				break;
			case T__18:
				enterOuterAlt(_localctx, 2);
				{
				setState(74);
				lidsSection();
				}
				break;
			case T__27:
				enterOuterAlt(_localctx, 3);
				{
				setState(75);
				particlesSection();
				}
				break;
			case T__42:
				enterOuterAlt(_localctx, 4);
				{
				setState(76);
				packingSection();
				}
				break;
			case T__67:
				enterOuterAlt(_localctx, 5);
				{
				setState(77);
				exportSection();
				}
				break;
			case T__81:
				enterOuterAlt(_localctx, 6);
				{
				setState(78);
				cfdSection();
				}
				break;
			case T__91:
				enterOuterAlt(_localctx, 7);
				{
				setState(79);
				geometrySection();
				}
				break;
			case T__96:
				enterOuterAlt(_localctx, 8);
				{
				setState(80);
				generationSection();
				}
				break;
			case T__100:
				enterOuterAlt(_localctx, 9);
				{
				setState(81);
				sliceSection();
				}
				break;
			case T__110:
				enterOuterAlt(_localctx, 10);
				{
				setState(82);
				statistical2dSection();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class BedSectionContext extends ParserRuleContext {
		public List<BedPropertyContext> bedProperty() {
			return getRuleContexts(BedPropertyContext.class);
		}
		public BedPropertyContext bedProperty(int i) {
			return getRuleContext(BedPropertyContext.class,i);
		}
		public BedSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_bedSection; }
	}

	public final BedSectionContext bedSection() throws RecognitionException {
		BedSectionContext _localctx = new BedSectionContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_bedSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(85);
			match(T__0);
			setState(86);
			match(T__1);
			setState(88); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(87);
				bedProperty();
				}
				}
				setState(90); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__3) | (1L << T__6) | (1L << T__7) | (1L << T__8) | (1L << T__9) | (1L << T__10) | (1L << T__11) | (1L << T__12))) != 0) );
			setState(92);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class BedPropertyContext extends ParserRuleContext {
		public BedPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_bedProperty; }
	 
		public BedPropertyContext() { }
		public void copyFrom(BedPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class BedWallThicknessContext extends BedPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public BedWallThicknessContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedMaterialContext extends BedPropertyContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public BedMaterialContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedInternalCylinderModeContext extends BedPropertyContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public BedInternalCylinderModeContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedClearanceContext extends BedPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public BedClearanceContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedDiameterContext extends BedPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public BedDiameterContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedRoughnessContext extends BedPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public BedRoughnessContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedVisibilityBlockContext extends BedPropertyContext {
		public List<VisibilityPropertyContext> visibilityProperty() {
			return getRuleContexts(VisibilityPropertyContext.class);
		}
		public VisibilityPropertyContext visibilityProperty(int i) {
			return getRuleContext(VisibilityPropertyContext.class,i);
		}
		public BedVisibilityBlockContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class BedHeightContext extends BedPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public BedHeightContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}

	public final BedPropertyContext bedProperty() throws RecognitionException {
		BedPropertyContext _localctx = new BedPropertyContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_bedProperty);
		int _la;
		try {
			setState(136);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__3:
				_localctx = new BedDiameterContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(94);
				match(T__3);
				setState(95);
				match(T__4);
				setState(96);
				match(NUMBER);
				setState(97);
				match(UNIT);
				setState(98);
				match(T__5);
				}
				break;
			case T__6:
				_localctx = new BedHeightContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(99);
				match(T__6);
				setState(100);
				match(T__4);
				setState(101);
				match(NUMBER);
				setState(102);
				match(UNIT);
				setState(103);
				match(T__5);
				}
				break;
			case T__7:
				_localctx = new BedWallThicknessContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(104);
				match(T__7);
				setState(105);
				match(T__4);
				setState(106);
				match(NUMBER);
				setState(107);
				match(UNIT);
				setState(108);
				match(T__5);
				}
				break;
			case T__8:
				_localctx = new BedClearanceContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(109);
				match(T__8);
				setState(110);
				match(T__4);
				setState(111);
				match(NUMBER);
				setState(112);
				match(UNIT);
				setState(113);
				match(T__5);
				}
				break;
			case T__9:
				_localctx = new BedMaterialContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(114);
				match(T__9);
				setState(115);
				match(T__4);
				setState(116);
				match(STRING);
				setState(117);
				match(T__5);
				}
				break;
			case T__10:
				_localctx = new BedRoughnessContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(118);
				match(T__10);
				setState(119);
				match(T__4);
				setState(120);
				match(NUMBER);
				setState(121);
				match(UNIT);
				setState(122);
				match(T__5);
				}
				break;
			case T__11:
				_localctx = new BedInternalCylinderModeContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(123);
				match(T__11);
				setState(124);
				match(T__4);
				setState(125);
				match(STRING);
				setState(126);
				match(T__5);
				}
				break;
			case T__12:
				_localctx = new BedVisibilityBlockContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(127);
				match(T__12);
				setState(128);
				match(T__1);
				setState(130); 
				_errHandler.sync(this);
				_la = _input.LA(1);
				do {
					{
					{
					setState(129);
					visibilityProperty();
					}
					}
					setState(132); 
					_errHandler.sync(this);
					_la = _input.LA(1);
				} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__13) | (1L << T__14) | (1L << T__15) | (1L << T__16) | (1L << T__17))) != 0) );
				setState(134);
				match(T__2);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VisibilityPropertyContext extends ParserRuleContext {
		public VisibilityPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_visibilityProperty; }
	 
		public VisibilityPropertyContext() { }
		public void copyFrom(VisibilityPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class VisShowOuterContext extends VisibilityPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public VisShowOuterContext(VisibilityPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class VisShowInternalContext extends VisibilityPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public VisShowInternalContext(VisibilityPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class VisShowParticlesContext extends VisibilityPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public VisShowParticlesContext(VisibilityPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class VisShowBooleanToolsContext extends VisibilityPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public VisShowBooleanToolsContext(VisibilityPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class VisExportBooleanToolsContext extends VisibilityPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public VisExportBooleanToolsContext(VisibilityPropertyContext ctx) { copyFrom(ctx); }
	}

	public final VisibilityPropertyContext visibilityProperty() throws RecognitionException {
		VisibilityPropertyContext _localctx = new VisibilityPropertyContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_visibilityProperty);
		try {
			setState(158);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__13:
				_localctx = new VisShowOuterContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(138);
				match(T__13);
				setState(139);
				match(T__4);
				setState(140);
				match(BOOLEAN);
				setState(141);
				match(T__5);
				}
				break;
			case T__14:
				_localctx = new VisShowInternalContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(142);
				match(T__14);
				setState(143);
				match(T__4);
				setState(144);
				match(BOOLEAN);
				setState(145);
				match(T__5);
				}
				break;
			case T__15:
				_localctx = new VisShowParticlesContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(146);
				match(T__15);
				setState(147);
				match(T__4);
				setState(148);
				match(BOOLEAN);
				setState(149);
				match(T__5);
				}
				break;
			case T__16:
				_localctx = new VisShowBooleanToolsContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(150);
				match(T__16);
				setState(151);
				match(T__4);
				setState(152);
				match(BOOLEAN);
				setState(153);
				match(T__5);
				}
				break;
			case T__17:
				_localctx = new VisExportBooleanToolsContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(154);
				match(T__17);
				setState(155);
				match(T__4);
				setState(156);
				match(BOOLEAN);
				setState(157);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class LidsSectionContext extends ParserRuleContext {
		public List<LidsPropertyContext> lidsProperty() {
			return getRuleContexts(LidsPropertyContext.class);
		}
		public LidsPropertyContext lidsProperty(int i) {
			return getRuleContext(LidsPropertyContext.class,i);
		}
		public LidsSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lidsSection; }
	}

	public final LidsSectionContext lidsSection() throws RecognitionException {
		LidsSectionContext _localctx = new LidsSectionContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_lidsSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(160);
			match(T__18);
			setState(161);
			match(T__1);
			setState(163); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(162);
				lidsProperty();
				}
				}
				setState(165); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__19) | (1L << T__20) | (1L << T__21) | (1L << T__22) | (1L << T__23))) != 0) );
			setState(167);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class LidsPropertyContext extends ParserRuleContext {
		public LidsPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lidsProperty; }
	 
		public LidsPropertyContext() { }
		public void copyFrom(LidsPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class LidsSealClearanceContext extends LidsPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public LidsSealClearanceContext(LidsPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class LidsTopTypeContext extends LidsPropertyContext {
		public LidTypeContext lidType() {
			return getRuleContext(LidTypeContext.class,0);
		}
		public LidsTopTypeContext(LidsPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class LidsBottomTypeContext extends LidsPropertyContext {
		public LidTypeContext lidType() {
			return getRuleContext(LidTypeContext.class,0);
		}
		public LidsBottomTypeContext(LidsPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class LidsBottomThicknessContext extends LidsPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public LidsBottomThicknessContext(LidsPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class LidsTopThicknessContext extends LidsPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public LidsTopThicknessContext(LidsPropertyContext ctx) { copyFrom(ctx); }
	}

	public final LidsPropertyContext lidsProperty() throws RecognitionException {
		LidsPropertyContext _localctx = new LidsPropertyContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_lidsProperty);
		try {
			setState(194);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__19:
				_localctx = new LidsTopTypeContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(169);
				match(T__19);
				setState(170);
				match(T__4);
				setState(171);
				lidType();
				setState(172);
				match(T__5);
				}
				break;
			case T__20:
				_localctx = new LidsBottomTypeContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(174);
				match(T__20);
				setState(175);
				match(T__4);
				setState(176);
				lidType();
				setState(177);
				match(T__5);
				}
				break;
			case T__21:
				_localctx = new LidsTopThicknessContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(179);
				match(T__21);
				setState(180);
				match(T__4);
				setState(181);
				match(NUMBER);
				setState(182);
				match(UNIT);
				setState(183);
				match(T__5);
				}
				break;
			case T__22:
				_localctx = new LidsBottomThicknessContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(184);
				match(T__22);
				setState(185);
				match(T__4);
				setState(186);
				match(NUMBER);
				setState(187);
				match(UNIT);
				setState(188);
				match(T__5);
				}
				break;
			case T__23:
				_localctx = new LidsSealClearanceContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(189);
				match(T__23);
				setState(190);
				match(T__4);
				setState(191);
				match(NUMBER);
				setState(192);
				match(UNIT);
				setState(193);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class LidTypeContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public LidTypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lidType; }
	}

	public final LidTypeContext lidType() throws RecognitionException {
		LidTypeContext _localctx = new LidTypeContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_lidType);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(196);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__24) | (1L << T__25) | (1L << T__26))) != 0) || _la==STRING) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ParticlesSectionContext extends ParserRuleContext {
		public List<ParticlesPropertyContext> particlesProperty() {
			return getRuleContexts(ParticlesPropertyContext.class);
		}
		public ParticlesPropertyContext particlesProperty(int i) {
			return getRuleContext(ParticlesPropertyContext.class,i);
		}
		public ParticlesSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_particlesSection; }
	}

	public final ParticlesSectionContext particlesSection() throws RecognitionException {
		ParticlesSectionContext _localctx = new ParticlesSectionContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_particlesSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(198);
			match(T__27);
			setState(199);
			match(T__1);
			setState(201); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(200);
				particlesProperty();
				}
				}
				setState(203); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__3) | (1L << T__28) | (1L << T__29) | (1L << T__30) | (1L << T__31) | (1L << T__32) | (1L << T__33) | (1L << T__34) | (1L << T__35) | (1L << T__36) | (1L << T__37) | (1L << T__38))) != 0) );
			setState(205);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ParticlesPropertyContext extends ParserRuleContext {
		public ParticlesPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_particlesProperty; }
	 
		public ParticlesPropertyContext() { }
		public void copyFrom(ParticlesPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class ParticlesSeedContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesSeedContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesCountContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesCountContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesLinearDampingContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesLinearDampingContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesDensityContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public ParticlesDensityContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesKindContext extends ParticlesPropertyContext {
		public ParticleKindContext particleKind() {
			return getRuleContext(ParticleKindContext.class,0);
		}
		public ParticlesKindContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesDiameterContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public ParticlesDiameterContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesFrictionContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesFrictionContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesMassContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public ParticlesMassContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesTargetPorosityContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesTargetPorosityContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesRollingFrictionContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesRollingFrictionContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesAngularDampingContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesAngularDampingContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ParticlesRestitutionContext extends ParticlesPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ParticlesRestitutionContext(ParticlesPropertyContext ctx) { copyFrom(ctx); }
	}

	public final ParticlesPropertyContext particlesProperty() throws RecognitionException {
		ParticlesPropertyContext _localctx = new ParticlesPropertyContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_particlesProperty);
		try {
			setState(259);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__28:
				_localctx = new ParticlesKindContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(207);
				match(T__28);
				setState(208);
				match(T__4);
				setState(209);
				particleKind();
				setState(210);
				match(T__5);
				}
				break;
			case T__3:
				_localctx = new ParticlesDiameterContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(212);
				match(T__3);
				setState(213);
				match(T__4);
				setState(214);
				match(NUMBER);
				setState(215);
				match(UNIT);
				setState(216);
				match(T__5);
				}
				break;
			case T__29:
				_localctx = new ParticlesCountContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(217);
				match(T__29);
				setState(218);
				match(T__4);
				setState(219);
				match(NUMBER);
				setState(220);
				match(T__5);
				}
				break;
			case T__30:
				_localctx = new ParticlesTargetPorosityContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(221);
				match(T__30);
				setState(222);
				match(T__4);
				setState(223);
				match(NUMBER);
				setState(224);
				match(T__5);
				}
				break;
			case T__31:
				_localctx = new ParticlesDensityContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(225);
				match(T__31);
				setState(226);
				match(T__4);
				setState(227);
				match(NUMBER);
				setState(228);
				match(UNIT);
				setState(229);
				match(T__5);
				}
				break;
			case T__32:
				_localctx = new ParticlesMassContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(230);
				match(T__32);
				setState(231);
				match(T__4);
				setState(232);
				match(NUMBER);
				setState(233);
				match(UNIT);
				setState(234);
				match(T__5);
				}
				break;
			case T__33:
				_localctx = new ParticlesRestitutionContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(235);
				match(T__33);
				setState(236);
				match(T__4);
				setState(237);
				match(NUMBER);
				setState(238);
				match(T__5);
				}
				break;
			case T__34:
				_localctx = new ParticlesFrictionContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(239);
				match(T__34);
				setState(240);
				match(T__4);
				setState(241);
				match(NUMBER);
				setState(242);
				match(T__5);
				}
				break;
			case T__35:
				_localctx = new ParticlesRollingFrictionContext(_localctx);
				enterOuterAlt(_localctx, 9);
				{
				setState(243);
				match(T__35);
				setState(244);
				match(T__4);
				setState(245);
				match(NUMBER);
				setState(246);
				match(T__5);
				}
				break;
			case T__36:
				_localctx = new ParticlesLinearDampingContext(_localctx);
				enterOuterAlt(_localctx, 10);
				{
				setState(247);
				match(T__36);
				setState(248);
				match(T__4);
				setState(249);
				match(NUMBER);
				setState(250);
				match(T__5);
				}
				break;
			case T__37:
				_localctx = new ParticlesAngularDampingContext(_localctx);
				enterOuterAlt(_localctx, 11);
				{
				setState(251);
				match(T__37);
				setState(252);
				match(T__4);
				setState(253);
				match(NUMBER);
				setState(254);
				match(T__5);
				}
				break;
			case T__38:
				_localctx = new ParticlesSeedContext(_localctx);
				enterOuterAlt(_localctx, 12);
				{
				setState(255);
				match(T__38);
				setState(256);
				match(T__4);
				setState(257);
				match(NUMBER);
				setState(258);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ParticleKindContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public ParticleKindContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_particleKind; }
	}

	public final ParticleKindContext particleKind() throws RecognitionException {
		ParticleKindContext _localctx = new ParticleKindContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_particleKind);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(261);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__39) | (1L << T__40) | (1L << T__41))) != 0) || _la==STRING) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PackingSectionContext extends ParserRuleContext {
		public List<PackingPropertyContext> packingProperty() {
			return getRuleContexts(PackingPropertyContext.class);
		}
		public PackingPropertyContext packingProperty(int i) {
			return getRuleContext(PackingPropertyContext.class,i);
		}
		public PackingSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_packingSection; }
	}

	public final PackingSectionContext packingSection() throws RecognitionException {
		PackingSectionContext _localctx = new PackingSectionContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_packingSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(263);
			match(T__42);
			setState(264);
			match(T__1);
			setState(266); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(265);
				packingProperty();
				}
				}
				setState(268); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__43) | (1L << T__44) | (1L << T__45) | (1L << T__46) | (1L << T__47) | (1L << T__48) | (1L << T__49) | (1L << T__50) | (1L << T__51) | (1L << T__52) | (1L << T__53) | (1L << T__54) | (1L << T__55) | (1L << T__56) | (1L << T__57) | (1L << T__58) | (1L << T__59) | (1L << T__60))) != 0) );
			setState(270);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PackingPropertyContext extends ParserRuleContext {
		public PackingPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_packingProperty; }
	 
		public PackingPropertyContext() { }
		public void copyFrom(PackingPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class PackingDampingContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingDampingContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingSphereLonContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingSphereLonContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingCollisionMarginContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingCollisionMarginContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingGapContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingGapContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingSubstepsContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingSubstepsContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingMaxTimeContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingMaxTimeContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingGravityContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingGravityContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingRandomSeedContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingRandomSeedContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingMaxAttemptsContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingMaxAttemptsContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingStrictValidationContext extends PackingPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public PackingStrictValidationContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingUseLegacyDropContext extends PackingPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public PackingUseLegacyDropContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingRestVelocityContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingRestVelocityContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingStepXContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingStepXContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingDemBlockContext extends PackingPropertyContext {
		public List<DemPropertyContext> demProperty() {
			return getRuleContexts(DemPropertyContext.class);
		}
		public DemPropertyContext demProperty(int i) {
			return getRuleContext(DemPropertyContext.class,i);
		}
		public PackingDemBlockContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingIterationsContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingIterationsContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingSphereLatContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingSphereLatContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingMeshSegmentosContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingMeshSegmentosContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingMethodPropContext extends PackingPropertyContext {
		public PackingMethodContext packingMethod() {
			return getRuleContext(PackingMethodContext.class,0);
		}
		public PackingMethodPropContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}

	public final PackingPropertyContext packingProperty() throws RecognitionException {
		PackingPropertyContext _localctx = new PackingPropertyContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_packingProperty);
		int _la;
		try {
			setState(356);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__43:
				_localctx = new PackingMethodPropContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(272);
				match(T__43);
				setState(273);
				match(T__4);
				setState(274);
				packingMethod();
				setState(275);
				match(T__5);
				}
				break;
			case T__44:
				_localctx = new PackingGravityContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(277);
				match(T__44);
				setState(278);
				match(T__4);
				setState(279);
				match(NUMBER);
				setState(280);
				match(UNIT);
				setState(281);
				match(T__5);
				}
				break;
			case T__45:
				_localctx = new PackingSubstepsContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(282);
				match(T__45);
				setState(283);
				match(T__4);
				setState(284);
				match(NUMBER);
				setState(285);
				match(T__5);
				}
				break;
			case T__46:
				_localctx = new PackingIterationsContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(286);
				match(T__46);
				setState(287);
				match(T__4);
				setState(288);
				match(NUMBER);
				setState(289);
				match(T__5);
				}
				break;
			case T__47:
				_localctx = new PackingDampingContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(290);
				match(T__47);
				setState(291);
				match(T__4);
				setState(292);
				match(NUMBER);
				setState(293);
				match(T__5);
				}
				break;
			case T__48:
				_localctx = new PackingRestVelocityContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(294);
				match(T__48);
				setState(295);
				match(T__4);
				setState(296);
				match(NUMBER);
				setState(297);
				match(UNIT);
				setState(298);
				match(T__5);
				}
				break;
			case T__49:
				_localctx = new PackingMaxTimeContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(299);
				match(T__49);
				setState(300);
				match(T__4);
				setState(301);
				match(NUMBER);
				setState(302);
				match(UNIT);
				setState(303);
				match(T__5);
				}
				break;
			case T__50:
				_localctx = new PackingCollisionMarginContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(304);
				match(T__50);
				setState(305);
				match(T__4);
				setState(306);
				match(NUMBER);
				setState(307);
				match(UNIT);
				setState(308);
				match(T__5);
				}
				break;
			case T__51:
				_localctx = new PackingGapContext(_localctx);
				enterOuterAlt(_localctx, 9);
				{
				setState(309);
				match(T__51);
				setState(310);
				match(T__4);
				setState(311);
				match(NUMBER);
				setState(312);
				match(UNIT);
				setState(313);
				match(T__5);
				}
				break;
			case T__52:
				_localctx = new PackingRandomSeedContext(_localctx);
				enterOuterAlt(_localctx, 10);
				{
				setState(314);
				match(T__52);
				setState(315);
				match(T__4);
				setState(316);
				match(NUMBER);
				setState(317);
				match(T__5);
				}
				break;
			case T__53:
				_localctx = new PackingMaxAttemptsContext(_localctx);
				enterOuterAlt(_localctx, 11);
				{
				setState(318);
				match(T__53);
				setState(319);
				match(T__4);
				setState(320);
				match(NUMBER);
				setState(321);
				match(T__5);
				}
				break;
			case T__54:
				_localctx = new PackingStrictValidationContext(_localctx);
				enterOuterAlt(_localctx, 12);
				{
				setState(322);
				match(T__54);
				setState(323);
				match(T__4);
				setState(324);
				match(BOOLEAN);
				setState(325);
				match(T__5);
				}
				break;
			case T__55:
				_localctx = new PackingStepXContext(_localctx);
				enterOuterAlt(_localctx, 13);
				{
				setState(326);
				match(T__55);
				setState(327);
				match(T__4);
				setState(328);
				match(NUMBER);
				setState(329);
				match(UNIT);
				setState(330);
				match(T__5);
				}
				break;
			case T__56:
				_localctx = new PackingMeshSegmentosContext(_localctx);
				enterOuterAlt(_localctx, 14);
				{
				setState(331);
				match(T__56);
				setState(332);
				match(T__4);
				setState(333);
				match(NUMBER);
				setState(334);
				match(T__5);
				}
				break;
			case T__57:
				_localctx = new PackingSphereLatContext(_localctx);
				enterOuterAlt(_localctx, 15);
				{
				setState(335);
				match(T__57);
				setState(336);
				match(T__4);
				setState(337);
				match(NUMBER);
				setState(338);
				match(T__5);
				}
				break;
			case T__58:
				_localctx = new PackingSphereLonContext(_localctx);
				enterOuterAlt(_localctx, 16);
				{
				setState(339);
				match(T__58);
				setState(340);
				match(T__4);
				setState(341);
				match(NUMBER);
				setState(342);
				match(T__5);
				}
				break;
			case T__59:
				_localctx = new PackingUseLegacyDropContext(_localctx);
				enterOuterAlt(_localctx, 17);
				{
				setState(343);
				match(T__59);
				setState(344);
				match(T__4);
				setState(345);
				match(BOOLEAN);
				setState(346);
				match(T__5);
				}
				break;
			case T__60:
				_localctx = new PackingDemBlockContext(_localctx);
				enterOuterAlt(_localctx, 18);
				{
				setState(347);
				match(T__60);
				setState(348);
				match(T__1);
				setState(350); 
				_errHandler.sync(this);
				_la = _input.LA(1);
				do {
					{
					{
					setState(349);
					demProperty();
					}
					}
					setState(352); 
					_errHandler.sync(this);
					_la = _input.LA(1);
				} while ( ((((_la - 34)) & ~0x3f) == 0 && ((1L << (_la - 34)) & ((1L << (T__33 - 34)) | (1L << (T__34 - 34)) | (1L << (T__38 - 34)) | (1L << (T__44 - 34)) | (1L << (T__47 - 34)) | (1L << (T__61 - 34)) | (1L << (T__62 - 34)) | (1L << (T__63 - 34)) | (1L << (T__64 - 34)) | (1L << (T__65 - 34)))) != 0) );
				setState(354);
				match(T__2);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DemPropertyContext extends ParserRuleContext {
		public DemPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_demProperty; }
	 
		public DemPropertyContext() { }
		public void copyFrom(DemPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class DemSeedContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public DemSeedContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemGravityContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public DemGravityContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemSettleThresholdContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public DemSettleThresholdContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemDampingContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public DemDampingContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemFrictionContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public DemFrictionContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemStepsContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public DemStepsContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemStiffnessContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public DemStiffnessContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemRestitutionContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public DemRestitutionContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemTimeStepContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public DemTimeStepContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class DemMaxVelocityContext extends DemPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public DemMaxVelocityContext(DemPropertyContext ctx) { copyFrom(ctx); }
	}

	public final DemPropertyContext demProperty() throws RecognitionException {
		DemPropertyContext _localctx = new DemPropertyContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_demProperty);
		try {
			setState(402);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__61:
				_localctx = new DemTimeStepContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(358);
				match(T__61);
				setState(359);
				match(T__4);
				setState(360);
				match(NUMBER);
				setState(361);
				match(UNIT);
				setState(362);
				match(T__5);
				}
				break;
			case T__62:
				_localctx = new DemStepsContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(363);
				match(T__62);
				setState(364);
				match(T__4);
				setState(365);
				match(NUMBER);
				setState(366);
				match(T__5);
				}
				break;
			case T__44:
				_localctx = new DemGravityContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(367);
				match(T__44);
				setState(368);
				match(T__4);
				setState(369);
				match(NUMBER);
				setState(370);
				match(UNIT);
				setState(371);
				match(T__5);
				}
				break;
			case T__63:
				_localctx = new DemStiffnessContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(372);
				match(T__63);
				setState(373);
				match(T__4);
				setState(374);
				match(NUMBER);
				setState(375);
				match(T__5);
				}
				break;
			case T__47:
				_localctx = new DemDampingContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(376);
				match(T__47);
				setState(377);
				match(T__4);
				setState(378);
				match(NUMBER);
				setState(379);
				match(T__5);
				}
				break;
			case T__34:
				_localctx = new DemFrictionContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(380);
				match(T__34);
				setState(381);
				match(T__4);
				setState(382);
				match(NUMBER);
				setState(383);
				match(T__5);
				}
				break;
			case T__33:
				_localctx = new DemRestitutionContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(384);
				match(T__33);
				setState(385);
				match(T__4);
				setState(386);
				match(NUMBER);
				setState(387);
				match(T__5);
				}
				break;
			case T__64:
				_localctx = new DemSettleThresholdContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(388);
				match(T__64);
				setState(389);
				match(T__4);
				setState(390);
				match(NUMBER);
				setState(391);
				match(UNIT);
				setState(392);
				match(T__5);
				}
				break;
			case T__65:
				_localctx = new DemMaxVelocityContext(_localctx);
				enterOuterAlt(_localctx, 9);
				{
				setState(393);
				match(T__65);
				setState(394);
				match(T__4);
				setState(395);
				match(NUMBER);
				setState(396);
				match(UNIT);
				setState(397);
				match(T__5);
				}
				break;
			case T__38:
				_localctx = new DemSeedContext(_localctx);
				enterOuterAlt(_localctx, 10);
				{
				setState(398);
				match(T__38);
				setState(399);
				match(T__4);
				setState(400);
				match(NUMBER);
				setState(401);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PackingMethodContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public PackingMethodContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_packingMethod; }
	}

	public final PackingMethodContext packingMethod() throws RecognitionException {
		PackingMethodContext _localctx = new PackingMethodContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_packingMethod);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(404);
			_la = _input.LA(1);
			if ( !(_la==T__66 || _la==STRING) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ExportSectionContext extends ParserRuleContext {
		public List<ExportPropertyContext> exportProperty() {
			return getRuleContexts(ExportPropertyContext.class);
		}
		public ExportPropertyContext exportProperty(int i) {
			return getRuleContext(ExportPropertyContext.class,i);
		}
		public ExportSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_exportSection; }
	}

	public final ExportSectionContext exportSection() throws RecognitionException {
		ExportSectionContext _localctx = new ExportSectionContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_exportSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(406);
			match(T__67);
			setState(407);
			match(T__1);
			setState(409); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(408);
				exportProperty();
				}
				}
				setState(411); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( ((((_la - 69)) & ~0x3f) == 0 && ((1L << (_la - 69)) & ((1L << (T__68 - 69)) | (1L << (T__71 - 69)) | (1L << (T__72 - 69)) | (1L << (T__73 - 69)) | (1L << (T__74 - 69)) | (1L << (T__75 - 69)) | (1L << (T__76 - 69)))) != 0) );
			setState(413);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ExportPropertyContext extends ParserRuleContext {
		public ExportPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_exportProperty; }
	 
		public ExportPropertyContext() { }
		public void copyFrom(ExportPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class ExportScaleContext extends ExportPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public ExportScaleContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ExportMergeDistanceContext extends ExportPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public ExportMergeDistanceContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ExportWallModeContext extends ExportPropertyContext {
		public WallModeContext wallMode() {
			return getRuleContext(WallModeContext.class,0);
		}
		public ExportWallModeContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ExportFluidModeContext extends ExportPropertyContext {
		public FluidModeContext fluidMode() {
			return getRuleContext(FluidModeContext.class,0);
		}
		public ExportFluidModeContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ExportManifoldCheckContext extends ExportPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public ExportManifoldCheckContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ExportFormatsContext extends ExportPropertyContext {
		public FormatListContext formatList() {
			return getRuleContext(FormatListContext.class,0);
		}
		public ExportFormatsContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class ExportUnitsContext extends ExportPropertyContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public ExportUnitsContext(ExportPropertyContext ctx) { copyFrom(ctx); }
	}

	public final ExportPropertyContext exportProperty() throws RecognitionException {
		ExportPropertyContext _localctx = new ExportPropertyContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_exportProperty);
		try {
			setState(449);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__68:
				_localctx = new ExportFormatsContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(415);
				match(T__68);
				setState(416);
				match(T__4);
				setState(417);
				match(T__69);
				setState(418);
				formatList();
				setState(419);
				match(T__70);
				setState(420);
				match(T__5);
				}
				break;
			case T__71:
				_localctx = new ExportUnitsContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(422);
				match(T__71);
				setState(423);
				match(T__4);
				setState(424);
				match(STRING);
				setState(425);
				match(T__5);
				}
				break;
			case T__72:
				_localctx = new ExportScaleContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(426);
				match(T__72);
				setState(427);
				match(T__4);
				setState(428);
				match(NUMBER);
				setState(429);
				match(T__5);
				}
				break;
			case T__73:
				_localctx = new ExportWallModeContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(430);
				match(T__73);
				setState(431);
				match(T__4);
				setState(432);
				wallMode();
				setState(433);
				match(T__5);
				}
				break;
			case T__74:
				_localctx = new ExportFluidModeContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(435);
				match(T__74);
				setState(436);
				match(T__4);
				setState(437);
				fluidMode();
				setState(438);
				match(T__5);
				}
				break;
			case T__75:
				_localctx = new ExportManifoldCheckContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(440);
				match(T__75);
				setState(441);
				match(T__4);
				setState(442);
				match(BOOLEAN);
				setState(443);
				match(T__5);
				}
				break;
			case T__76:
				_localctx = new ExportMergeDistanceContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(444);
				match(T__76);
				setState(445);
				match(T__4);
				setState(446);
				match(NUMBER);
				setState(447);
				match(UNIT);
				setState(448);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FormatListContext extends ParserRuleContext {
		public List<TerminalNode> STRING() { return getTokens(BedParser.STRING); }
		public TerminalNode STRING(int i) {
			return getToken(BedParser.STRING, i);
		}
		public FormatListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_formatList; }
	}

	public final FormatListContext formatList() throws RecognitionException {
		FormatListContext _localctx = new FormatListContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_formatList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(451);
			match(STRING);
			setState(456);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==T__77) {
				{
				{
				setState(452);
				match(T__77);
				setState(453);
				match(STRING);
				}
				}
				setState(458);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class WallModeContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public WallModeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_wallMode; }
	}

	public final WallModeContext wallMode() throws RecognitionException {
		WallModeContext _localctx = new WallModeContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_wallMode);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(459);
			_la = _input.LA(1);
			if ( !(((((_la - 79)) & ~0x3f) == 0 && ((1L << (_la - 79)) & ((1L << (T__78 - 79)) | (1L << (T__79 - 79)) | (1L << (STRING - 79)))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FluidModeContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public FluidModeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_fluidMode; }
	}

	public final FluidModeContext fluidMode() throws RecognitionException {
		FluidModeContext _localctx = new FluidModeContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_fluidMode);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(461);
			_la = _input.LA(1);
			if ( !(_la==T__26 || _la==T__80 || _la==STRING) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CfdSectionContext extends ParserRuleContext {
		public List<CfdPropertyContext> cfdProperty() {
			return getRuleContexts(CfdPropertyContext.class);
		}
		public CfdPropertyContext cfdProperty(int i) {
			return getRuleContext(CfdPropertyContext.class,i);
		}
		public CfdSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_cfdSection; }
	}

	public final CfdSectionContext cfdSection() throws RecognitionException {
		CfdSectionContext _localctx = new CfdSectionContext(_ctx, getState());
		enterRule(_localctx, 40, RULE_cfdSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(463);
			match(T__81);
			setState(464);
			match(T__1);
			setState(466); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(465);
				cfdProperty();
				}
				}
				setState(468); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( ((((_la - 83)) & ~0x3f) == 0 && ((1L << (_la - 83)) & ((1L << (T__82 - 83)) | (1L << (T__83 - 83)) | (1L << (T__84 - 83)) | (1L << (T__85 - 83)) | (1L << (T__86 - 83)) | (1L << (T__87 - 83)) | (1L << (T__88 - 83)))) != 0) );
			setState(470);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CfdPropertyContext extends ParserRuleContext {
		public CfdPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_cfdProperty; }
	 
		public CfdPropertyContext() { }
		public void copyFrom(CfdPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class CfdInletVelocityContext extends CfdPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public CfdInletVelocityContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class CfdWriteFieldsContext extends CfdPropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public CfdWriteFieldsContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class CfdMaxIterationsContext extends CfdPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public CfdMaxIterationsContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class CfdConvergenceCriteriaContext extends CfdPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public CfdConvergenceCriteriaContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class CfdFluidViscosityContext extends CfdPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public CfdFluidViscosityContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class CfdRegimePropContext extends CfdPropertyContext {
		public CfdRegimeContext cfdRegime() {
			return getRuleContext(CfdRegimeContext.class,0);
		}
		public CfdRegimePropContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class CfdFluidDensityContext extends CfdPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public CfdFluidDensityContext(CfdPropertyContext ctx) { copyFrom(ctx); }
	}

	public final CfdPropertyContext cfdProperty() throws RecognitionException {
		CfdPropertyContext _localctx = new CfdPropertyContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_cfdProperty);
		try {
			setState(504);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__82:
				_localctx = new CfdRegimePropContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(472);
				match(T__82);
				setState(473);
				match(T__4);
				setState(474);
				cfdRegime();
				setState(475);
				match(T__5);
				}
				break;
			case T__83:
				_localctx = new CfdInletVelocityContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(477);
				match(T__83);
				setState(478);
				match(T__4);
				setState(479);
				match(NUMBER);
				setState(480);
				match(UNIT);
				setState(481);
				match(T__5);
				}
				break;
			case T__84:
				_localctx = new CfdFluidDensityContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(482);
				match(T__84);
				setState(483);
				match(T__4);
				setState(484);
				match(NUMBER);
				setState(485);
				match(UNIT);
				setState(486);
				match(T__5);
				}
				break;
			case T__85:
				_localctx = new CfdFluidViscosityContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(487);
				match(T__85);
				setState(488);
				match(T__4);
				setState(489);
				match(NUMBER);
				setState(490);
				match(UNIT);
				setState(491);
				match(T__5);
				}
				break;
			case T__86:
				_localctx = new CfdMaxIterationsContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(492);
				match(T__86);
				setState(493);
				match(T__4);
				setState(494);
				match(NUMBER);
				setState(495);
				match(T__5);
				}
				break;
			case T__87:
				_localctx = new CfdConvergenceCriteriaContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(496);
				match(T__87);
				setState(497);
				match(T__4);
				setState(498);
				match(NUMBER);
				setState(499);
				match(T__5);
				}
				break;
			case T__88:
				_localctx = new CfdWriteFieldsContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(500);
				match(T__88);
				setState(501);
				match(T__4);
				setState(502);
				match(BOOLEAN);
				setState(503);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CfdRegimeContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public CfdRegimeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_cfdRegime; }
	}

	public final CfdRegimeContext cfdRegime() throws RecognitionException {
		CfdRegimeContext _localctx = new CfdRegimeContext(_ctx, getState());
		enterRule(_localctx, 44, RULE_cfdRegime);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(506);
			_la = _input.LA(1);
			if ( !(((((_la - 90)) & ~0x3f) == 0 && ((1L << (_la - 90)) & ((1L << (T__89 - 90)) | (1L << (T__90 - 90)) | (1L << (STRING - 90)))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class GeometrySectionContext extends ParserRuleContext {
		public List<GeometryPropertyContext> geometryProperty() {
			return getRuleContexts(GeometryPropertyContext.class);
		}
		public GeometryPropertyContext geometryProperty(int i) {
			return getRuleContext(GeometryPropertyContext.class,i);
		}
		public GeometrySectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_geometrySection; }
	}

	public final GeometrySectionContext geometrySection() throws RecognitionException {
		GeometrySectionContext _localctx = new GeometrySectionContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_geometrySection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(508);
			match(T__91);
			setState(509);
			match(T__1);
			setState(511); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(510);
				geometryProperty();
				}
				}
				setState(513); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__92 );
			setState(515);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class GeometryPropertyContext extends ParserRuleContext {
		public GeometryPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_geometryProperty; }
	 
		public GeometryPropertyContext() { }
		public void copyFrom(GeometryPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class GeometryModePropContext extends GeometryPropertyContext {
		public GeometryModeContext geometryMode() {
			return getRuleContext(GeometryModeContext.class,0);
		}
		public GeometryModePropContext(GeometryPropertyContext ctx) { copyFrom(ctx); }
	}

	public final GeometryPropertyContext geometryProperty() throws RecognitionException {
		GeometryPropertyContext _localctx = new GeometryPropertyContext(_ctx, getState());
		enterRule(_localctx, 48, RULE_geometryProperty);
		try {
			_localctx = new GeometryModePropContext(_localctx);
			enterOuterAlt(_localctx, 1);
			{
			setState(517);
			match(T__92);
			setState(518);
			match(T__4);
			setState(519);
			geometryMode();
			setState(520);
			match(T__5);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class GeometryModeContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public GeometryModeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_geometryMode; }
	}

	public final GeometryModeContext geometryMode() throws RecognitionException {
		GeometryModeContext _localctx = new GeometryModeContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_geometryMode);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(522);
			_la = _input.LA(1);
			if ( !(((((_la - 94)) & ~0x3f) == 0 && ((1L << (_la - 94)) & ((1L << (T__93 - 94)) | (1L << (T__94 - 94)) | (1L << (T__95 - 94)) | (1L << (STRING - 94)))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class GenerationSectionContext extends ParserRuleContext {
		public List<GenerationPropertyContext> generationProperty() {
			return getRuleContexts(GenerationPropertyContext.class);
		}
		public GenerationPropertyContext generationProperty(int i) {
			return getRuleContext(GenerationPropertyContext.class,i);
		}
		public GenerationSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_generationSection; }
	}

	public final GenerationSectionContext generationSection() throws RecognitionException {
		GenerationSectionContext _localctx = new GenerationSectionContext(_ctx, getState());
		enterRule(_localctx, 52, RULE_generationSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(524);
			match(T__96);
			setState(525);
			match(T__1);
			setState(527); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(526);
				generationProperty();
				}
				}
				setState(529); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__97 );
			setState(531);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class GenerationPropertyContext extends ParserRuleContext {
		public GenerationPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_generationProperty; }
	 
		public GenerationPropertyContext() { }
		public void copyFrom(GenerationPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class GenerationBackendPropContext extends GenerationPropertyContext {
		public GenerationBackendContext generationBackend() {
			return getRuleContext(GenerationBackendContext.class,0);
		}
		public GenerationBackendPropContext(GenerationPropertyContext ctx) { copyFrom(ctx); }
	}

	public final GenerationPropertyContext generationProperty() throws RecognitionException {
		GenerationPropertyContext _localctx = new GenerationPropertyContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_generationProperty);
		try {
			_localctx = new GenerationBackendPropContext(_localctx);
			enterOuterAlt(_localctx, 1);
			{
			setState(533);
			match(T__97);
			setState(534);
			match(T__4);
			setState(535);
			generationBackend();
			setState(536);
			match(T__5);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class GenerationBackendContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public GenerationBackendContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_generationBackend; }
	}

	public final GenerationBackendContext generationBackend() throws RecognitionException {
		GenerationBackendContext _localctx = new GenerationBackendContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_generationBackend);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(538);
			_la = _input.LA(1);
			if ( !(((((_la - 99)) & ~0x3f) == 0 && ((1L << (_la - 99)) & ((1L << (T__98 - 99)) | (1L << (T__99 - 99)) | (1L << (STRING - 99)))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class SliceSectionContext extends ParserRuleContext {
		public List<SlicePropertyContext> sliceProperty() {
			return getRuleContexts(SlicePropertyContext.class);
		}
		public SlicePropertyContext sliceProperty(int i) {
			return getRuleContext(SlicePropertyContext.class,i);
		}
		public SliceSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_sliceSection; }
	}

	public final SliceSectionContext sliceSection() throws RecognitionException {
		SliceSectionContext _localctx = new SliceSectionContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_sliceSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(540);
			match(T__100);
			setState(541);
			match(T__1);
			setState(543); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(542);
				sliceProperty();
				}
				}
				setState(545); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( ((((_la - 102)) & ~0x3f) == 0 && ((1L << (_la - 102)) & ((1L << (T__101 - 102)) | (1L << (T__102 - 102)) | (1L << (T__103 - 102)) | (1L << (T__104 - 102)) | (1L << (T__105 - 102)) | (1L << (T__106 - 102)) | (1L << (T__107 - 102)) | (1L << (T__108 - 102)) | (1L << (T__109 - 102)))) != 0) );
			setState(547);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class SlicePropertyContext extends ParserRuleContext {
		public SlicePropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_sliceProperty; }
	 
		public SlicePropertyContext() { }
		public void copyFrom(SlicePropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class SliceThicknessContext extends SlicePropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public SliceThicknessContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SlicePreservePackingContext extends SlicePropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public SlicePreservePackingContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SliceEnabledContext extends SlicePropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public SliceEnabledContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SliceParticlePolicyContext extends SlicePropertyContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public SliceParticlePolicyContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SlicePositionContext extends SlicePropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public SlicePositionContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SliceMinParticleRadiusContext extends SlicePropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public SliceMinParticleRadiusContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SliceAxisContext extends SlicePropertyContext {
		public TerminalNode STRING() { return getToken(BedParser.STRING, 0); }
		public SliceAxisContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SliceDebugGizmosContext extends SlicePropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public SliceDebugGizmosContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}
	public static class SliceKeepOnlyContext extends SlicePropertyContext {
		public TerminalNode BOOLEAN() { return getToken(BedParser.BOOLEAN, 0); }
		public SliceKeepOnlyContext(SlicePropertyContext ctx) { copyFrom(ctx); }
	}

	public final SlicePropertyContext sliceProperty() throws RecognitionException {
		SlicePropertyContext _localctx = new SlicePropertyContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_sliceProperty);
		try {
			setState(588);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__101:
				_localctx = new SliceEnabledContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(549);
				match(T__101);
				setState(550);
				match(T__4);
				setState(551);
				match(BOOLEAN);
				setState(552);
				match(T__5);
				}
				break;
			case T__102:
				_localctx = new SliceThicknessContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(553);
				match(T__102);
				setState(554);
				match(T__4);
				setState(555);
				match(NUMBER);
				setState(556);
				match(UNIT);
				setState(557);
				match(T__5);
				}
				break;
			case T__103:
				_localctx = new SliceAxisContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(558);
				match(T__103);
				setState(559);
				match(T__4);
				setState(560);
				match(STRING);
				setState(561);
				match(T__5);
				}
				break;
			case T__104:
				_localctx = new SlicePositionContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(562);
				match(T__104);
				setState(563);
				match(T__4);
				setState(564);
				match(NUMBER);
				setState(565);
				match(UNIT);
				setState(566);
				match(T__5);
				}
				break;
			case T__105:
				_localctx = new SliceKeepOnlyContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(567);
				match(T__105);
				setState(568);
				match(T__4);
				setState(569);
				match(BOOLEAN);
				setState(570);
				match(T__5);
				}
				break;
			case T__106:
				_localctx = new SlicePreservePackingContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(571);
				match(T__106);
				setState(572);
				match(T__4);
				setState(573);
				match(BOOLEAN);
				setState(574);
				match(T__5);
				}
				break;
			case T__107:
				_localctx = new SliceParticlePolicyContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(575);
				match(T__107);
				setState(576);
				match(T__4);
				setState(577);
				match(STRING);
				setState(578);
				match(T__5);
				}
				break;
			case T__108:
				_localctx = new SliceDebugGizmosContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(579);
				match(T__108);
				setState(580);
				match(T__4);
				setState(581);
				match(BOOLEAN);
				setState(582);
				match(T__5);
				}
				break;
			case T__109:
				_localctx = new SliceMinParticleRadiusContext(_localctx);
				enterOuterAlt(_localctx, 9);
				{
				setState(583);
				match(T__109);
				setState(584);
				match(T__4);
				setState(585);
				match(NUMBER);
				setState(586);
				match(UNIT);
				setState(587);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Statistical2dSectionContext extends ParserRuleContext {
		public List<Statistical2dPropertyContext> statistical2dProperty() {
			return getRuleContexts(Statistical2dPropertyContext.class);
		}
		public Statistical2dPropertyContext statistical2dProperty(int i) {
			return getRuleContext(Statistical2dPropertyContext.class,i);
		}
		public Statistical2dSectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statistical2dSection; }
	}

	public final Statistical2dSectionContext statistical2dSection() throws RecognitionException {
		Statistical2dSectionContext _localctx = new Statistical2dSectionContext(_ctx, getState());
		enterRule(_localctx, 62, RULE_statistical2dSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(590);
			match(T__110);
			setState(591);
			match(T__1);
			setState(593); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(592);
				statistical2dProperty();
				}
				}
				setState(595); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__30 || _la==T__38 || ((((_la - 112)) & ~0x3f) == 0 && ((1L << (_la - 112)) & ((1L << (T__111 - 112)) | (1L << (T__112 - 112)) | (1L << (T__113 - 112)) | (1L << (T__114 - 112)) | (1L << (T__115 - 112)))) != 0) );
			setState(597);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Statistical2dPropertyContext extends ParserRuleContext {
		public Statistical2dPropertyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statistical2dProperty; }
	 
		public Statistical2dPropertyContext() { }
		public void copyFrom(Statistical2dPropertyContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class StatDomainWidthContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public StatDomainWidthContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class StatDomainHeightContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public StatDomainHeightContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class StatToleranceContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public StatToleranceContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class StatTargetPorosityContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public StatTargetPorosityContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class StatSliceThicknessContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public StatSliceThicknessContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class StatMaxAttemptsContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public StatMaxAttemptsContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class StatSeedContext extends Statistical2dPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public StatSeedContext(Statistical2dPropertyContext ctx) { copyFrom(ctx); }
	}

	public final Statistical2dPropertyContext statistical2dProperty() throws RecognitionException {
		Statistical2dPropertyContext _localctx = new Statistical2dPropertyContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_statistical2dProperty);
		try {
			setState(630);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__111:
				_localctx = new StatDomainWidthContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(599);
				match(T__111);
				setState(600);
				match(T__4);
				setState(601);
				match(NUMBER);
				setState(602);
				match(UNIT);
				setState(603);
				match(T__5);
				}
				break;
			case T__112:
				_localctx = new StatDomainHeightContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(604);
				match(T__112);
				setState(605);
				match(T__4);
				setState(606);
				match(NUMBER);
				setState(607);
				match(UNIT);
				setState(608);
				match(T__5);
				}
				break;
			case T__30:
				_localctx = new StatTargetPorosityContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(609);
				match(T__30);
				setState(610);
				match(T__4);
				setState(611);
				match(NUMBER);
				setState(612);
				match(T__5);
				}
				break;
			case T__113:
				_localctx = new StatToleranceContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(613);
				match(T__113);
				setState(614);
				match(T__4);
				setState(615);
				match(NUMBER);
				setState(616);
				match(T__5);
				}
				break;
			case T__114:
				_localctx = new StatMaxAttemptsContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(617);
				match(T__114);
				setState(618);
				match(T__4);
				setState(619);
				match(NUMBER);
				setState(620);
				match(T__5);
				}
				break;
			case T__115:
				_localctx = new StatSliceThicknessContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(621);
				match(T__115);
				setState(622);
				match(T__4);
				setState(623);
				match(NUMBER);
				setState(624);
				match(UNIT);
				setState(625);
				match(T__5);
				}
				break;
			case T__38:
				_localctx = new StatSeedContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(626);
				match(T__38);
				setState(627);
				match(T__4);
				setState(628);
				match(NUMBER);
				setState(629);
				match(T__5);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3~\u027b\4\2\t\2\4"+
		"\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t"+
		"\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31\t\31"+
		"\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36\4\37\t\37\4 \t \4!"+
		"\t!\4\"\t\"\3\2\6\2F\n\2\r\2\16\2G\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3"+
		"\3\3\3\3\3\3\5\3V\n\3\3\4\3\4\3\4\6\4[\n\4\r\4\16\4\\\3\4\3\4\3\5\3\5"+
		"\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3"+
		"\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\6\5"+
		"\u0085\n\5\r\5\16\5\u0086\3\5\3\5\5\5\u008b\n\5\3\6\3\6\3\6\3\6\3\6\3"+
		"\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\5\6\u00a1\n"+
		"\6\3\7\3\7\3\7\6\7\u00a6\n\7\r\7\16\7\u00a7\3\7\3\7\3\b\3\b\3\b\3\b\3"+
		"\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b"+
		"\3\b\3\b\3\b\5\b\u00c5\n\b\3\t\3\t\3\n\3\n\3\n\6\n\u00cc\n\n\r\n\16\n"+
		"\u00cd\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13"+
		"\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13"+
		"\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13"+
		"\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\5\13"+
		"\u0106\n\13\3\f\3\f\3\r\3\r\3\r\6\r\u010d\n\r\r\r\16\r\u010e\3\r\3\r\3"+
		"\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3"+
		"\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3"+
		"\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3"+
		"\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3"+
		"\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3"+
		"\16\3\16\3\16\3\16\3\16\3\16\3\16\3\16\6\16\u0161\n\16\r\16\16\16\u0162"+
		"\3\16\3\16\5\16\u0167\n\16\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17"+
		"\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17"+
		"\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17"+
		"\3\17\3\17\3\17\3\17\3\17\3\17\3\17\5\17\u0195\n\17\3\20\3\20\3\21\3\21"+
		"\3\21\6\21\u019c\n\21\r\21\16\21\u019d\3\21\3\21\3\22\3\22\3\22\3\22\3"+
		"\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3"+
		"\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3"+
		"\22\3\22\5\22\u01c4\n\22\3\23\3\23\3\23\7\23\u01c9\n\23\f\23\16\23\u01cc"+
		"\13\23\3\24\3\24\3\25\3\25\3\26\3\26\3\26\6\26\u01d5\n\26\r\26\16\26\u01d6"+
		"\3\26\3\26\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27"+
		"\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27"+
		"\3\27\3\27\3\27\3\27\3\27\3\27\5\27\u01fb\n\27\3\30\3\30\3\31\3\31\3\31"+
		"\6\31\u0202\n\31\r\31\16\31\u0203\3\31\3\31\3\32\3\32\3\32\3\32\3\32\3"+
		"\33\3\33\3\34\3\34\3\34\6\34\u0212\n\34\r\34\16\34\u0213\3\34\3\34\3\35"+
		"\3\35\3\35\3\35\3\35\3\36\3\36\3\37\3\37\3\37\6\37\u0222\n\37\r\37\16"+
		"\37\u0223\3\37\3\37\3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3"+
		" \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \3 \5"+
		" \u024f\n \3!\3!\3!\6!\u0254\n!\r!\16!\u0255\3!\3!\3\"\3\"\3\"\3\"\3\""+
		"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3"+
		"\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\5\"\u0279\n\"\3\"\2\2#\2\4\6\b\n\f"+
		"\16\20\22\24\26\30\32\34\36 \"$&(*,.\60\62\64\668:<>@B\2\n\4\2\33\35z"+
		"z\4\2*,zz\4\2EEzz\4\2QRzz\5\2\35\35SSzz\4\2\\]zz\4\2`bzz\4\2efzz\2\u02be"+
		"\2E\3\2\2\2\4U\3\2\2\2\6W\3\2\2\2\b\u008a\3\2\2\2\n\u00a0\3\2\2\2\f\u00a2"+
		"\3\2\2\2\16\u00c4\3\2\2\2\20\u00c6\3\2\2\2\22\u00c8\3\2\2\2\24\u0105\3"+
		"\2\2\2\26\u0107\3\2\2\2\30\u0109\3\2\2\2\32\u0166\3\2\2\2\34\u0194\3\2"+
		"\2\2\36\u0196\3\2\2\2 \u0198\3\2\2\2\"\u01c3\3\2\2\2$\u01c5\3\2\2\2&\u01cd"+
		"\3\2\2\2(\u01cf\3\2\2\2*\u01d1\3\2\2\2,\u01fa\3\2\2\2.\u01fc\3\2\2\2\60"+
		"\u01fe\3\2\2\2\62\u0207\3\2\2\2\64\u020c\3\2\2\2\66\u020e\3\2\2\28\u0217"+
		"\3\2\2\2:\u021c\3\2\2\2<\u021e\3\2\2\2>\u024e\3\2\2\2@\u0250\3\2\2\2B"+
		"\u0278\3\2\2\2DF\5\4\3\2ED\3\2\2\2FG\3\2\2\2GE\3\2\2\2GH\3\2\2\2HI\3\2"+
		"\2\2IJ\7\2\2\3J\3\3\2\2\2KV\5\6\4\2LV\5\f\7\2MV\5\22\n\2NV\5\30\r\2OV"+
		"\5 \21\2PV\5*\26\2QV\5\60\31\2RV\5\66\34\2SV\5<\37\2TV\5@!\2UK\3\2\2\2"+
		"UL\3\2\2\2UM\3\2\2\2UN\3\2\2\2UO\3\2\2\2UP\3\2\2\2UQ\3\2\2\2UR\3\2\2\2"+
		"US\3\2\2\2UT\3\2\2\2V\5\3\2\2\2WX\7\3\2\2XZ\7\4\2\2Y[\5\b\5\2ZY\3\2\2"+
		"\2[\\\3\2\2\2\\Z\3\2\2\2\\]\3\2\2\2]^\3\2\2\2^_\7\5\2\2_\7\3\2\2\2`a\7"+
		"\6\2\2ab\7\7\2\2bc\7w\2\2cd\7y\2\2d\u008b\7\b\2\2ef\7\t\2\2fg\7\7\2\2"+
		"gh\7w\2\2hi\7y\2\2i\u008b\7\b\2\2jk\7\n\2\2kl\7\7\2\2lm\7w\2\2mn\7y\2"+
		"\2n\u008b\7\b\2\2op\7\13\2\2pq\7\7\2\2qr\7w\2\2rs\7y\2\2s\u008b\7\b\2"+
		"\2tu\7\f\2\2uv\7\7\2\2vw\7z\2\2w\u008b\7\b\2\2xy\7\r\2\2yz\7\7\2\2z{\7"+
		"w\2\2{|\7y\2\2|\u008b\7\b\2\2}~\7\16\2\2~\177\7\7\2\2\177\u0080\7z\2\2"+
		"\u0080\u008b\7\b\2\2\u0081\u0082\7\17\2\2\u0082\u0084\7\4\2\2\u0083\u0085"+
		"\5\n\6\2\u0084\u0083\3\2\2\2\u0085\u0086\3\2\2\2\u0086\u0084\3\2\2\2\u0086"+
		"\u0087\3\2\2\2\u0087\u0088\3\2\2\2\u0088\u0089\7\5\2\2\u0089\u008b\3\2"+
		"\2\2\u008a`\3\2\2\2\u008ae\3\2\2\2\u008aj\3\2\2\2\u008ao\3\2\2\2\u008a"+
		"t\3\2\2\2\u008ax\3\2\2\2\u008a}\3\2\2\2\u008a\u0081\3\2\2\2\u008b\t\3"+
		"\2\2\2\u008c\u008d\7\20\2\2\u008d\u008e\7\7\2\2\u008e\u008f\7{\2\2\u008f"+
		"\u00a1\7\b\2\2\u0090\u0091\7\21\2\2\u0091\u0092\7\7\2\2\u0092\u0093\7"+
		"{\2\2\u0093\u00a1\7\b\2\2\u0094\u0095\7\22\2\2\u0095\u0096\7\7\2\2\u0096"+
		"\u0097\7{\2\2\u0097\u00a1\7\b\2\2\u0098\u0099\7\23\2\2\u0099\u009a\7\7"+
		"\2\2\u009a\u009b\7{\2\2\u009b\u00a1\7\b\2\2\u009c\u009d\7\24\2\2\u009d"+
		"\u009e\7\7\2\2\u009e\u009f\7{\2\2\u009f\u00a1\7\b\2\2\u00a0\u008c\3\2"+
		"\2\2\u00a0\u0090\3\2\2\2\u00a0\u0094\3\2\2\2\u00a0\u0098\3\2\2\2\u00a0"+
		"\u009c\3\2\2\2\u00a1\13\3\2\2\2\u00a2\u00a3\7\25\2\2\u00a3\u00a5\7\4\2"+
		"\2\u00a4\u00a6\5\16\b\2\u00a5\u00a4\3\2\2\2\u00a6\u00a7\3\2\2\2\u00a7"+
		"\u00a5\3\2\2\2\u00a7\u00a8\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a9\u00aa\7\5"+
		"\2\2\u00aa\r\3\2\2\2\u00ab\u00ac\7\26\2\2\u00ac\u00ad\7\7\2\2\u00ad\u00ae"+
		"\5\20\t\2\u00ae\u00af\7\b\2\2\u00af\u00c5\3\2\2\2\u00b0\u00b1\7\27\2\2"+
		"\u00b1\u00b2\7\7\2\2\u00b2\u00b3\5\20\t\2\u00b3\u00b4\7\b\2\2\u00b4\u00c5"+
		"\3\2\2\2\u00b5\u00b6\7\30\2\2\u00b6\u00b7\7\7\2\2\u00b7\u00b8\7w\2\2\u00b8"+
		"\u00b9\7y\2\2\u00b9\u00c5\7\b\2\2\u00ba\u00bb\7\31\2\2\u00bb\u00bc\7\7"+
		"\2\2\u00bc\u00bd\7w\2\2\u00bd\u00be\7y\2\2\u00be\u00c5\7\b\2\2\u00bf\u00c0"+
		"\7\32\2\2\u00c0\u00c1\7\7\2\2\u00c1\u00c2\7w\2\2\u00c2\u00c3\7y\2\2\u00c3"+
		"\u00c5\7\b\2\2\u00c4\u00ab\3\2\2\2\u00c4\u00b0\3\2\2\2\u00c4\u00b5\3\2"+
		"\2\2\u00c4\u00ba\3\2\2\2\u00c4\u00bf\3\2\2\2\u00c5\17\3\2\2\2\u00c6\u00c7"+
		"\t\2\2\2\u00c7\21\3\2\2\2\u00c8\u00c9\7\36\2\2\u00c9\u00cb\7\4\2\2\u00ca"+
		"\u00cc\5\24\13\2\u00cb\u00ca\3\2\2\2\u00cc\u00cd\3\2\2\2\u00cd\u00cb\3"+
		"\2\2\2\u00cd\u00ce\3\2\2\2\u00ce\u00cf\3\2\2\2\u00cf\u00d0\7\5\2\2\u00d0"+
		"\23\3\2\2\2\u00d1\u00d2\7\37\2\2\u00d2\u00d3\7\7\2\2\u00d3\u00d4\5\26"+
		"\f\2\u00d4\u00d5\7\b\2\2\u00d5\u0106\3\2\2\2\u00d6\u00d7\7\6\2\2\u00d7"+
		"\u00d8\7\7\2\2\u00d8\u00d9\7w\2\2\u00d9\u00da\7y\2\2\u00da\u0106\7\b\2"+
		"\2\u00db\u00dc\7 \2\2\u00dc\u00dd\7\7\2\2\u00dd\u00de\7w\2\2\u00de\u0106"+
		"\7\b\2\2\u00df\u00e0\7!\2\2\u00e0\u00e1\7\7\2\2\u00e1\u00e2\7w\2\2\u00e2"+
		"\u0106\7\b\2\2\u00e3\u00e4\7\"\2\2\u00e4\u00e5\7\7\2\2\u00e5\u00e6\7w"+
		"\2\2\u00e6\u00e7\7y\2\2\u00e7\u0106\7\b\2\2\u00e8\u00e9\7#\2\2\u00e9\u00ea"+
		"\7\7\2\2\u00ea\u00eb\7w\2\2\u00eb\u00ec\7y\2\2\u00ec\u0106\7\b\2\2\u00ed"+
		"\u00ee\7$\2\2\u00ee\u00ef\7\7\2\2\u00ef\u00f0\7w\2\2\u00f0\u0106\7\b\2"+
		"\2\u00f1\u00f2\7%\2\2\u00f2\u00f3\7\7\2\2\u00f3\u00f4\7w\2\2\u00f4\u0106"+
		"\7\b\2\2\u00f5\u00f6\7&\2\2\u00f6\u00f7\7\7\2\2\u00f7\u00f8\7w\2\2\u00f8"+
		"\u0106\7\b\2\2\u00f9\u00fa\7\'\2\2\u00fa\u00fb\7\7\2\2\u00fb\u00fc\7w"+
		"\2\2\u00fc\u0106\7\b\2\2\u00fd\u00fe\7(\2\2\u00fe\u00ff\7\7\2\2\u00ff"+
		"\u0100\7w\2\2\u0100\u0106\7\b\2\2\u0101\u0102\7)\2\2\u0102\u0103\7\7\2"+
		"\2\u0103\u0104\7w\2\2\u0104\u0106\7\b\2\2\u0105\u00d1\3\2\2\2\u0105\u00d6"+
		"\3\2\2\2\u0105\u00db\3\2\2\2\u0105\u00df\3\2\2\2\u0105\u00e3\3\2\2\2\u0105"+
		"\u00e8\3\2\2\2\u0105\u00ed\3\2\2\2\u0105\u00f1\3\2\2\2\u0105\u00f5\3\2"+
		"\2\2\u0105\u00f9\3\2\2\2\u0105\u00fd\3\2\2\2\u0105\u0101\3\2\2\2\u0106"+
		"\25\3\2\2\2\u0107\u0108\t\3\2\2\u0108\27\3\2\2\2\u0109\u010a\7-\2\2\u010a"+
		"\u010c\7\4\2\2\u010b\u010d\5\32\16\2\u010c\u010b\3\2\2\2\u010d\u010e\3"+
		"\2\2\2\u010e\u010c\3\2\2\2\u010e\u010f\3\2\2\2\u010f\u0110\3\2\2\2\u0110"+
		"\u0111\7\5\2\2\u0111\31\3\2\2\2\u0112\u0113\7.\2\2\u0113\u0114\7\7\2\2"+
		"\u0114\u0115\5\36\20\2\u0115\u0116\7\b\2\2\u0116\u0167\3\2\2\2\u0117\u0118"+
		"\7/\2\2\u0118\u0119\7\7\2\2\u0119\u011a\7w\2\2\u011a\u011b\7y\2\2\u011b"+
		"\u0167\7\b\2\2\u011c\u011d\7\60\2\2\u011d\u011e\7\7\2\2\u011e\u011f\7"+
		"w\2\2\u011f\u0167\7\b\2\2\u0120\u0121\7\61\2\2\u0121\u0122\7\7\2\2\u0122"+
		"\u0123\7w\2\2\u0123\u0167\7\b\2\2\u0124\u0125\7\62\2\2\u0125\u0126\7\7"+
		"\2\2\u0126\u0127\7w\2\2\u0127\u0167\7\b\2\2\u0128\u0129\7\63\2\2\u0129"+
		"\u012a\7\7\2\2\u012a\u012b\7w\2\2\u012b\u012c\7y\2\2\u012c\u0167\7\b\2"+
		"\2\u012d\u012e\7\64\2\2\u012e\u012f\7\7\2\2\u012f\u0130\7w\2\2\u0130\u0131"+
		"\7y\2\2\u0131\u0167\7\b\2\2\u0132\u0133\7\65\2\2\u0133\u0134\7\7\2\2\u0134"+
		"\u0135\7w\2\2\u0135\u0136\7y\2\2\u0136\u0167\7\b\2\2\u0137\u0138\7\66"+
		"\2\2\u0138\u0139\7\7\2\2\u0139\u013a\7w\2\2\u013a\u013b\7y\2\2\u013b\u0167"+
		"\7\b\2\2\u013c\u013d\7\67\2\2\u013d\u013e\7\7\2\2\u013e\u013f\7w\2\2\u013f"+
		"\u0167\7\b\2\2\u0140\u0141\78\2\2\u0141\u0142\7\7\2\2\u0142\u0143\7w\2"+
		"\2\u0143\u0167\7\b\2\2\u0144\u0145\79\2\2\u0145\u0146\7\7\2\2\u0146\u0147"+
		"\7{\2\2\u0147\u0167\7\b\2\2\u0148\u0149\7:\2\2\u0149\u014a\7\7\2\2\u014a"+
		"\u014b\7w\2\2\u014b\u014c\7y\2\2\u014c\u0167\7\b\2\2\u014d\u014e\7;\2"+
		"\2\u014e\u014f\7\7\2\2\u014f\u0150\7w\2\2\u0150\u0167\7\b\2\2\u0151\u0152"+
		"\7<\2\2\u0152\u0153\7\7\2\2\u0153\u0154\7w\2\2\u0154\u0167\7\b\2\2\u0155"+
		"\u0156\7=\2\2\u0156\u0157\7\7\2\2\u0157\u0158\7w\2\2\u0158\u0167\7\b\2"+
		"\2\u0159\u015a\7>\2\2\u015a\u015b\7\7\2\2\u015b\u015c\7{\2\2\u015c\u0167"+
		"\7\b\2\2\u015d\u015e\7?\2\2\u015e\u0160\7\4\2\2\u015f\u0161\5\34\17\2"+
		"\u0160\u015f\3\2\2\2\u0161\u0162\3\2\2\2\u0162\u0160\3\2\2\2\u0162\u0163"+
		"\3\2\2\2\u0163\u0164\3\2\2\2\u0164\u0165\7\5\2\2\u0165\u0167\3\2\2\2\u0166"+
		"\u0112\3\2\2\2\u0166\u0117\3\2\2\2\u0166\u011c\3\2\2\2\u0166\u0120\3\2"+
		"\2\2\u0166\u0124\3\2\2\2\u0166\u0128\3\2\2\2\u0166\u012d\3\2\2\2\u0166"+
		"\u0132\3\2\2\2\u0166\u0137\3\2\2\2\u0166\u013c\3\2\2\2\u0166\u0140\3\2"+
		"\2\2\u0166\u0144\3\2\2\2\u0166\u0148\3\2\2\2\u0166\u014d\3\2\2\2\u0166"+
		"\u0151\3\2\2\2\u0166\u0155\3\2\2\2\u0166\u0159\3\2\2\2\u0166\u015d\3\2"+
		"\2\2\u0167\33\3\2\2\2\u0168\u0169\7@\2\2\u0169\u016a\7\7\2\2\u016a\u016b"+
		"\7w\2\2\u016b\u016c\7y\2\2\u016c\u0195\7\b\2\2\u016d\u016e\7A\2\2\u016e"+
		"\u016f\7\7\2\2\u016f\u0170\7w\2\2\u0170\u0195\7\b\2\2\u0171\u0172\7/\2"+
		"\2\u0172\u0173\7\7\2\2\u0173\u0174\7w\2\2\u0174\u0175\7y\2\2\u0175\u0195"+
		"\7\b\2\2\u0176\u0177\7B\2\2\u0177\u0178\7\7\2\2\u0178\u0179\7w\2\2\u0179"+
		"\u0195\7\b\2\2\u017a\u017b\7\62\2\2\u017b\u017c\7\7\2\2\u017c\u017d\7"+
		"w\2\2\u017d\u0195\7\b\2\2\u017e\u017f\7%\2\2\u017f\u0180\7\7\2\2\u0180"+
		"\u0181\7w\2\2\u0181\u0195\7\b\2\2\u0182\u0183\7$\2\2\u0183\u0184\7\7\2"+
		"\2\u0184\u0185\7w\2\2\u0185\u0195\7\b\2\2\u0186\u0187\7C\2\2\u0187\u0188"+
		"\7\7\2\2\u0188\u0189\7w\2\2\u0189\u018a\7y\2\2\u018a\u0195\7\b\2\2\u018b"+
		"\u018c\7D\2\2\u018c\u018d\7\7\2\2\u018d\u018e\7w\2\2\u018e\u018f\7y\2"+
		"\2\u018f\u0195\7\b\2\2\u0190\u0191\7)\2\2\u0191\u0192\7\7\2\2\u0192\u0193"+
		"\7w\2\2\u0193\u0195\7\b\2\2\u0194\u0168\3\2\2\2\u0194\u016d\3\2\2\2\u0194"+
		"\u0171\3\2\2\2\u0194\u0176\3\2\2\2\u0194\u017a\3\2\2\2\u0194\u017e\3\2"+
		"\2\2\u0194\u0182\3\2\2\2\u0194\u0186\3\2\2\2\u0194\u018b\3\2\2\2\u0194"+
		"\u0190\3\2\2\2\u0195\35\3\2\2\2\u0196\u0197\t\4\2\2\u0197\37\3\2\2\2\u0198"+
		"\u0199\7F\2\2\u0199\u019b\7\4\2\2\u019a\u019c\5\"\22\2\u019b\u019a\3\2"+
		"\2\2\u019c\u019d\3\2\2\2\u019d\u019b\3\2\2\2\u019d\u019e\3\2\2\2\u019e"+
		"\u019f\3\2\2\2\u019f\u01a0\7\5\2\2\u01a0!\3\2\2\2\u01a1\u01a2\7G\2\2\u01a2"+
		"\u01a3\7\7\2\2\u01a3\u01a4\7H\2\2\u01a4\u01a5\5$\23\2\u01a5\u01a6\7I\2"+
		"\2\u01a6\u01a7\7\b\2\2\u01a7\u01c4\3\2\2\2\u01a8\u01a9\7J\2\2\u01a9\u01aa"+
		"\7\7\2\2\u01aa\u01ab\7z\2\2\u01ab\u01c4\7\b\2\2\u01ac\u01ad\7K\2\2\u01ad"+
		"\u01ae\7\7\2\2\u01ae\u01af\7w\2\2\u01af\u01c4\7\b\2\2\u01b0\u01b1\7L\2"+
		"\2\u01b1\u01b2\7\7\2\2\u01b2\u01b3\5&\24\2\u01b3\u01b4\7\b\2\2\u01b4\u01c4"+
		"\3\2\2\2\u01b5\u01b6\7M\2\2\u01b6\u01b7\7\7\2\2\u01b7\u01b8\5(\25\2\u01b8"+
		"\u01b9\7\b\2\2\u01b9\u01c4\3\2\2\2\u01ba\u01bb\7N\2\2\u01bb\u01bc\7\7"+
		"\2\2\u01bc\u01bd\7{\2\2\u01bd\u01c4\7\b\2\2\u01be\u01bf\7O\2\2\u01bf\u01c0"+
		"\7\7\2\2\u01c0\u01c1\7w\2\2\u01c1\u01c2\7y\2\2\u01c2\u01c4\7\b\2\2\u01c3"+
		"\u01a1\3\2\2\2\u01c3\u01a8\3\2\2\2\u01c3\u01ac\3\2\2\2\u01c3\u01b0\3\2"+
		"\2\2\u01c3\u01b5\3\2\2\2\u01c3\u01ba\3\2\2\2\u01c3\u01be\3\2\2\2\u01c4"+
		"#\3\2\2\2\u01c5\u01ca\7z\2\2\u01c6\u01c7\7P\2\2\u01c7\u01c9\7z\2\2\u01c8"+
		"\u01c6\3\2\2\2\u01c9\u01cc\3\2\2\2\u01ca\u01c8\3\2\2\2\u01ca\u01cb\3\2"+
		"\2\2\u01cb%\3\2\2\2\u01cc\u01ca\3\2\2\2\u01cd\u01ce\t\5\2\2\u01ce\'\3"+
		"\2\2\2\u01cf\u01d0\t\6\2\2\u01d0)\3\2\2\2\u01d1\u01d2\7T\2\2\u01d2\u01d4"+
		"\7\4\2\2\u01d3\u01d5\5,\27\2\u01d4\u01d3\3\2\2\2\u01d5\u01d6\3\2\2\2\u01d6"+
		"\u01d4\3\2\2\2\u01d6\u01d7\3\2\2\2\u01d7\u01d8\3\2\2\2\u01d8\u01d9\7\5"+
		"\2\2\u01d9+\3\2\2\2\u01da\u01db\7U\2\2\u01db\u01dc\7\7\2\2\u01dc\u01dd"+
		"\5.\30\2\u01dd\u01de\7\b\2\2\u01de\u01fb\3\2\2\2\u01df\u01e0\7V\2\2\u01e0"+
		"\u01e1\7\7\2\2\u01e1\u01e2\7w\2\2\u01e2\u01e3\7y\2\2\u01e3\u01fb\7\b\2"+
		"\2\u01e4\u01e5\7W\2\2\u01e5\u01e6\7\7\2\2\u01e6\u01e7\7w\2\2\u01e7\u01e8"+
		"\7y\2\2\u01e8\u01fb\7\b\2\2\u01e9\u01ea\7X\2\2\u01ea\u01eb\7\7\2\2\u01eb"+
		"\u01ec\7w\2\2\u01ec\u01ed\7y\2\2\u01ed\u01fb\7\b\2\2\u01ee\u01ef\7Y\2"+
		"\2\u01ef\u01f0\7\7\2\2\u01f0\u01f1\7w\2\2\u01f1\u01fb\7\b\2\2\u01f2\u01f3"+
		"\7Z\2\2\u01f3\u01f4\7\7\2\2\u01f4\u01f5\7w\2\2\u01f5\u01fb\7\b\2\2\u01f6"+
		"\u01f7\7[\2\2\u01f7\u01f8\7\7\2\2\u01f8\u01f9\7{\2\2\u01f9\u01fb\7\b\2"+
		"\2\u01fa\u01da\3\2\2\2\u01fa\u01df\3\2\2\2\u01fa\u01e4\3\2\2\2\u01fa\u01e9"+
		"\3\2\2\2\u01fa\u01ee\3\2\2\2\u01fa\u01f2\3\2\2\2\u01fa\u01f6\3\2\2\2\u01fb"+
		"-\3\2\2\2\u01fc\u01fd\t\7\2\2\u01fd/\3\2\2\2\u01fe\u01ff\7^\2\2\u01ff"+
		"\u0201\7\4\2\2\u0200\u0202\5\62\32\2\u0201\u0200\3\2\2\2\u0202\u0203\3"+
		"\2\2\2\u0203\u0201\3\2\2\2\u0203\u0204\3\2\2\2\u0204\u0205\3\2\2\2\u0205"+
		"\u0206\7\5\2\2\u0206\61\3\2\2\2\u0207\u0208\7_\2\2\u0208\u0209\7\7\2\2"+
		"\u0209\u020a\5\64\33\2\u020a\u020b\7\b\2\2\u020b\63\3\2\2\2\u020c\u020d"+
		"\t\b\2\2\u020d\65\3\2\2\2\u020e\u020f\7c\2\2\u020f\u0211\7\4\2\2\u0210"+
		"\u0212\58\35\2\u0211\u0210\3\2\2\2\u0212\u0213\3\2\2\2\u0213\u0211\3\2"+
		"\2\2\u0213\u0214\3\2\2\2\u0214\u0215\3\2\2\2\u0215\u0216\7\5\2\2\u0216"+
		"\67\3\2\2\2\u0217\u0218\7d\2\2\u0218\u0219\7\7\2\2\u0219\u021a\5:\36\2"+
		"\u021a\u021b\7\b\2\2\u021b9\3\2\2\2\u021c\u021d\t\t\2\2\u021d;\3\2\2\2"+
		"\u021e\u021f\7g\2\2\u021f\u0221\7\4\2\2\u0220\u0222\5> \2\u0221\u0220"+
		"\3\2\2\2\u0222\u0223\3\2\2\2\u0223\u0221\3\2\2\2\u0223\u0224\3\2\2\2\u0224"+
		"\u0225\3\2\2\2\u0225\u0226\7\5\2\2\u0226=\3\2\2\2\u0227\u0228\7h\2\2\u0228"+
		"\u0229\7\7\2\2\u0229\u022a\7{\2\2\u022a\u024f\7\b\2\2\u022b\u022c\7i\2"+
		"\2\u022c\u022d\7\7\2\2\u022d\u022e\7w\2\2\u022e\u022f\7y\2\2\u022f\u024f"+
		"\7\b\2\2\u0230\u0231\7j\2\2\u0231\u0232\7\7\2\2\u0232\u0233\7z\2\2\u0233"+
		"\u024f\7\b\2\2\u0234\u0235\7k\2\2\u0235\u0236\7\7\2\2\u0236\u0237\7w\2"+
		"\2\u0237\u0238\7y\2\2\u0238\u024f\7\b\2\2\u0239\u023a\7l\2\2\u023a\u023b"+
		"\7\7\2\2\u023b\u023c\7{\2\2\u023c\u024f\7\b\2\2\u023d\u023e\7m\2\2\u023e"+
		"\u023f\7\7\2\2\u023f\u0240\7{\2\2\u0240\u024f\7\b\2\2\u0241\u0242\7n\2"+
		"\2\u0242\u0243\7\7\2\2\u0243\u0244\7z\2\2\u0244\u024f\7\b\2\2\u0245\u0246"+
		"\7o\2\2\u0246\u0247\7\7\2\2\u0247\u0248\7{\2\2\u0248\u024f\7\b\2\2\u0249"+
		"\u024a\7p\2\2\u024a\u024b\7\7\2\2\u024b\u024c\7w\2\2\u024c\u024d\7y\2"+
		"\2\u024d\u024f\7\b\2\2\u024e\u0227\3\2\2\2\u024e\u022b\3\2\2\2\u024e\u0230"+
		"\3\2\2\2\u024e\u0234\3\2\2\2\u024e\u0239\3\2\2\2\u024e\u023d\3\2\2\2\u024e"+
		"\u0241\3\2\2\2\u024e\u0245\3\2\2\2\u024e\u0249\3\2\2\2\u024f?\3\2\2\2"+
		"\u0250\u0251\7q\2\2\u0251\u0253\7\4\2\2\u0252\u0254\5B\"\2\u0253\u0252"+
		"\3\2\2\2\u0254\u0255\3\2\2\2\u0255\u0253\3\2\2\2\u0255\u0256\3\2\2\2\u0256"+
		"\u0257\3\2\2\2\u0257\u0258\7\5\2\2\u0258A\3\2\2\2\u0259\u025a\7r\2\2\u025a"+
		"\u025b\7\7\2\2\u025b\u025c\7w\2\2\u025c\u025d\7y\2\2\u025d\u0279\7\b\2"+
		"\2\u025e\u025f\7s\2\2\u025f\u0260\7\7\2\2\u0260\u0261\7w\2\2\u0261\u0262"+
		"\7y\2\2\u0262\u0279\7\b\2\2\u0263\u0264\7!\2\2\u0264\u0265\7\7\2\2\u0265"+
		"\u0266\7w\2\2\u0266\u0279\7\b\2\2\u0267\u0268\7t\2\2\u0268\u0269\7\7\2"+
		"\2\u0269\u026a\7w\2\2\u026a\u0279\7\b\2\2\u026b\u026c\7u\2\2\u026c\u026d"+
		"\7\7\2\2\u026d\u026e\7w\2\2\u026e\u0279\7\b\2\2\u026f\u0270\7v\2\2\u0270"+
		"\u0271\7\7\2\2\u0271\u0272\7w\2\2\u0272\u0273\7y\2\2\u0273\u0279\7\b\2"+
		"\2\u0274\u0275\7)\2\2\u0275\u0276\7\7\2\2\u0276\u0277\7w\2\2\u0277\u0279"+
		"\7\b\2\2\u0278\u0259\3\2\2\2\u0278\u025e\3\2\2\2\u0278\u0263\3\2\2\2\u0278"+
		"\u0267\3\2\2\2\u0278\u026b\3\2\2\2\u0278\u026f\3\2\2\2\u0278\u0274\3\2"+
		"\2\2\u0279C\3\2\2\2\33GU\\\u0086\u008a\u00a0\u00a7\u00c4\u00cd\u0105\u010e"+
		"\u0162\u0166\u0194\u019d\u01c3\u01ca\u01d6\u01fa\u0203\u0213\u0223\u024e"+
		"\u0255\u0278";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}