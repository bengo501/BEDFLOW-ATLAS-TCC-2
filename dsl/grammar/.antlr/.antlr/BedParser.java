// Generated from c:\Users\joxto\Downloads\BEDFLOW-ATLAS\dsl\grammar\.antlr\Bed.g4 by ANTLR 4.9.2
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
		T__66=67, T__67=68, T__68=69, NUMBER=70, INTEGER=71, UNIT=72, STRING=73, 
		BOOLEAN=74, WS=75, COMMENT=76, BLOCK_COMMENT=77;
	public static final int
		RULE_bedFile = 0, RULE_section = 1, RULE_bedSection = 2, RULE_bedProperty = 3, 
		RULE_lidsSection = 4, RULE_lidsProperty = 5, RULE_lidType = 6, RULE_particlesSection = 7, 
		RULE_particlesProperty = 8, RULE_particleKind = 9, RULE_packingSection = 10, 
		RULE_packingProperty = 11, RULE_packingMethod = 12, RULE_exportSection = 13, 
		RULE_exportProperty = 14, RULE_formatList = 15, RULE_wallMode = 16, RULE_fluidMode = 17, 
		RULE_cfdSection = 18, RULE_cfdProperty = 19, RULE_cfdRegime = 20;
	private static String[] makeRuleNames() {
		return new String[] {
			"bedFile", "section", "bedSection", "bedProperty", "lidsSection", "lidsProperty", 
			"lidType", "particlesSection", "particlesProperty", "particleKind", "packingSection", 
			"packingProperty", "packingMethod", "exportSection", "exportProperty", 
			"formatList", "wallMode", "fluidMode", "cfdSection", "cfdProperty", "cfdRegime"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'bed'", "'{'", "'}'", "'diameter'", "'='", "';'", "'height'", 
			"'wall_thickness'", "'clearance'", "'material'", "'roughness'", "'lids'", 
			"'top_type'", "'bottom_type'", "'top_thickness'", "'bottom_thickness'", 
			"'seal_clearance'", "'flat'", "'hemispherical'", "'none'", "'particles'", 
			"'kind'", "'count'", "'target_porosity'", "'density'", "'mass'", "'restitution'", 
			"'friction'", "'rolling_friction'", "'linear_damping'", "'angular_damping'", 
			"'seed'", "'sphere'", "'cube'", "'cylinder'", "'packing'", "'method'", 
			"'gravity'", "'substeps'", "'iterations'", "'damping'", "'rest_velocity'", 
			"'max_time'", "'collision_margin'", "'rigid_body'", "'export'", "'formats'", 
			"'['", "']'", "'units'", "'scale'", "'wall_mode'", "'fluid_mode'", "'manifold_check'", 
			"'merge_distance'", "','", "'surface'", "'solid'", "'cavity'", "'cfd'", 
			"'regime'", "'inlet_velocity'", "'fluid_density'", "'fluid_viscosity'", 
			"'max_iterations'", "'convergence_criteria'", "'write_fields'", "'laminar'", 
			"'turbulent_rans'"
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
			null, null, null, null, null, null, null, null, null, null, "NUMBER", 
			"INTEGER", "UNIT", "STRING", "BOOLEAN", "WS", "COMMENT", "BLOCK_COMMENT"
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
			setState(43); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(42);
				section();
				}
				}
				setState(45); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__0) | (1L << T__11) | (1L << T__20) | (1L << T__35) | (1L << T__45) | (1L << T__59))) != 0) );
			setState(47);
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
		public SectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_section; }
	}

	public final SectionContext section() throws RecognitionException {
		SectionContext _localctx = new SectionContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_section);
		try {
			setState(55);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__0:
				enterOuterAlt(_localctx, 1);
				{
				setState(49);
				bedSection();
				}
				break;
			case T__11:
				enterOuterAlt(_localctx, 2);
				{
				setState(50);
				lidsSection();
				}
				break;
			case T__20:
				enterOuterAlt(_localctx, 3);
				{
				setState(51);
				particlesSection();
				}
				break;
			case T__35:
				enterOuterAlt(_localctx, 4);
				{
				setState(52);
				packingSection();
				}
				break;
			case T__45:
				enterOuterAlt(_localctx, 5);
				{
				setState(53);
				exportSection();
				}
				break;
			case T__59:
				enterOuterAlt(_localctx, 6);
				{
				setState(54);
				cfdSection();
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
			setState(57);
			match(T__0);
			setState(58);
			match(T__1);
			setState(60); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(59);
				bedProperty();
				}
				}
				setState(62); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__3) | (1L << T__6) | (1L << T__7) | (1L << T__8) | (1L << T__9) | (1L << T__10))) != 0) );
			setState(64);
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
	public static class BedHeightContext extends BedPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public BedHeightContext(BedPropertyContext ctx) { copyFrom(ctx); }
	}

	public final BedPropertyContext bedProperty() throws RecognitionException {
		BedPropertyContext _localctx = new BedPropertyContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_bedProperty);
		try {
			setState(95);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__3:
				_localctx = new BedDiameterContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(66);
				match(T__3);
				setState(67);
				match(T__4);
				setState(68);
				match(NUMBER);
				setState(69);
				match(UNIT);
				setState(70);
				match(T__5);
				}
				break;
			case T__6:
				_localctx = new BedHeightContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(71);
				match(T__6);
				setState(72);
				match(T__4);
				setState(73);
				match(NUMBER);
				setState(74);
				match(UNIT);
				setState(75);
				match(T__5);
				}
				break;
			case T__7:
				_localctx = new BedWallThicknessContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(76);
				match(T__7);
				setState(77);
				match(T__4);
				setState(78);
				match(NUMBER);
				setState(79);
				match(UNIT);
				setState(80);
				match(T__5);
				}
				break;
			case T__8:
				_localctx = new BedClearanceContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(81);
				match(T__8);
				setState(82);
				match(T__4);
				setState(83);
				match(NUMBER);
				setState(84);
				match(UNIT);
				setState(85);
				match(T__5);
				}
				break;
			case T__9:
				_localctx = new BedMaterialContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(86);
				match(T__9);
				setState(87);
				match(T__4);
				setState(88);
				match(STRING);
				setState(89);
				match(T__5);
				}
				break;
			case T__10:
				_localctx = new BedRoughnessContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(90);
				match(T__10);
				setState(91);
				match(T__4);
				setState(92);
				match(NUMBER);
				setState(93);
				match(UNIT);
				setState(94);
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
		enterRule(_localctx, 8, RULE_lidsSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(97);
			match(T__11);
			setState(98);
			match(T__1);
			setState(100); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(99);
				lidsProperty();
				}
				}
				setState(102); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__12) | (1L << T__13) | (1L << T__14) | (1L << T__15) | (1L << T__16))) != 0) );
			setState(104);
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
		enterRule(_localctx, 10, RULE_lidsProperty);
		try {
			setState(131);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__12:
				_localctx = new LidsTopTypeContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(106);
				match(T__12);
				setState(107);
				match(T__4);
				setState(108);
				lidType();
				setState(109);
				match(T__5);
				}
				break;
			case T__13:
				_localctx = new LidsBottomTypeContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(111);
				match(T__13);
				setState(112);
				match(T__4);
				setState(113);
				lidType();
				setState(114);
				match(T__5);
				}
				break;
			case T__14:
				_localctx = new LidsTopThicknessContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(116);
				match(T__14);
				setState(117);
				match(T__4);
				setState(118);
				match(NUMBER);
				setState(119);
				match(UNIT);
				setState(120);
				match(T__5);
				}
				break;
			case T__15:
				_localctx = new LidsBottomThicknessContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(121);
				match(T__15);
				setState(122);
				match(T__4);
				setState(123);
				match(NUMBER);
				setState(124);
				match(UNIT);
				setState(125);
				match(T__5);
				}
				break;
			case T__16:
				_localctx = new LidsSealClearanceContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(126);
				match(T__16);
				setState(127);
				match(T__4);
				setState(128);
				match(NUMBER);
				setState(129);
				match(UNIT);
				setState(130);
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
		enterRule(_localctx, 12, RULE_lidType);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(133);
			_la = _input.LA(1);
			if ( !(((((_la - 18)) & ~0x3f) == 0 && ((1L << (_la - 18)) & ((1L << (T__17 - 18)) | (1L << (T__18 - 18)) | (1L << (T__19 - 18)) | (1L << (STRING - 18)))) != 0)) ) {
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
		enterRule(_localctx, 14, RULE_particlesSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(135);
			match(T__20);
			setState(136);
			match(T__1);
			setState(138); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(137);
				particlesProperty();
				}
				}
				setState(140); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__3) | (1L << T__21) | (1L << T__22) | (1L << T__23) | (1L << T__24) | (1L << T__25) | (1L << T__26) | (1L << T__27) | (1L << T__28) | (1L << T__29) | (1L << T__30) | (1L << T__31))) != 0) );
			setState(142);
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
		enterRule(_localctx, 16, RULE_particlesProperty);
		try {
			setState(196);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__21:
				_localctx = new ParticlesKindContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(144);
				match(T__21);
				setState(145);
				match(T__4);
				setState(146);
				particleKind();
				setState(147);
				match(T__5);
				}
				break;
			case T__3:
				_localctx = new ParticlesDiameterContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(149);
				match(T__3);
				setState(150);
				match(T__4);
				setState(151);
				match(NUMBER);
				setState(152);
				match(UNIT);
				setState(153);
				match(T__5);
				}
				break;
			case T__22:
				_localctx = new ParticlesCountContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(154);
				match(T__22);
				setState(155);
				match(T__4);
				setState(156);
				match(NUMBER);
				setState(157);
				match(T__5);
				}
				break;
			case T__23:
				_localctx = new ParticlesTargetPorosityContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(158);
				match(T__23);
				setState(159);
				match(T__4);
				setState(160);
				match(NUMBER);
				setState(161);
				match(T__5);
				}
				break;
			case T__24:
				_localctx = new ParticlesDensityContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(162);
				match(T__24);
				setState(163);
				match(T__4);
				setState(164);
				match(NUMBER);
				setState(165);
				match(UNIT);
				setState(166);
				match(T__5);
				}
				break;
			case T__25:
				_localctx = new ParticlesMassContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(167);
				match(T__25);
				setState(168);
				match(T__4);
				setState(169);
				match(NUMBER);
				setState(170);
				match(UNIT);
				setState(171);
				match(T__5);
				}
				break;
			case T__26:
				_localctx = new ParticlesRestitutionContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(172);
				match(T__26);
				setState(173);
				match(T__4);
				setState(174);
				match(NUMBER);
				setState(175);
				match(T__5);
				}
				break;
			case T__27:
				_localctx = new ParticlesFrictionContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(176);
				match(T__27);
				setState(177);
				match(T__4);
				setState(178);
				match(NUMBER);
				setState(179);
				match(T__5);
				}
				break;
			case T__28:
				_localctx = new ParticlesRollingFrictionContext(_localctx);
				enterOuterAlt(_localctx, 9);
				{
				setState(180);
				match(T__28);
				setState(181);
				match(T__4);
				setState(182);
				match(NUMBER);
				setState(183);
				match(T__5);
				}
				break;
			case T__29:
				_localctx = new ParticlesLinearDampingContext(_localctx);
				enterOuterAlt(_localctx, 10);
				{
				setState(184);
				match(T__29);
				setState(185);
				match(T__4);
				setState(186);
				match(NUMBER);
				setState(187);
				match(T__5);
				}
				break;
			case T__30:
				_localctx = new ParticlesAngularDampingContext(_localctx);
				enterOuterAlt(_localctx, 11);
				{
				setState(188);
				match(T__30);
				setState(189);
				match(T__4);
				setState(190);
				match(NUMBER);
				setState(191);
				match(T__5);
				}
				break;
			case T__31:
				_localctx = new ParticlesSeedContext(_localctx);
				enterOuterAlt(_localctx, 12);
				{
				setState(192);
				match(T__31);
				setState(193);
				match(T__4);
				setState(194);
				match(NUMBER);
				setState(195);
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
		enterRule(_localctx, 18, RULE_particleKind);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(198);
			_la = _input.LA(1);
			if ( !(((((_la - 33)) & ~0x3f) == 0 && ((1L << (_la - 33)) & ((1L << (T__32 - 33)) | (1L << (T__33 - 33)) | (1L << (T__34 - 33)) | (1L << (STRING - 33)))) != 0)) ) {
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
		enterRule(_localctx, 20, RULE_packingSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(200);
			match(T__35);
			setState(201);
			match(T__1);
			setState(203); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(202);
				packingProperty();
				}
				}
				setState(205); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__36) | (1L << T__37) | (1L << T__38) | (1L << T__39) | (1L << T__40) | (1L << T__41) | (1L << T__42) | (1L << T__43))) != 0) );
			setState(207);
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
	public static class PackingCollisionMarginContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingCollisionMarginContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingRestVelocityContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingRestVelocityContext(PackingPropertyContext ctx) { copyFrom(ctx); }
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
	public static class PackingIterationsContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public PackingIterationsContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingGravityContext extends PackingPropertyContext {
		public TerminalNode NUMBER() { return getToken(BedParser.NUMBER, 0); }
		public TerminalNode UNIT() { return getToken(BedParser.UNIT, 0); }
		public PackingGravityContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}
	public static class PackingMethodPropContext extends PackingPropertyContext {
		public PackingMethodContext packingMethod() {
			return getRuleContext(PackingMethodContext.class,0);
		}
		public PackingMethodPropContext(PackingPropertyContext ctx) { copyFrom(ctx); }
	}

	public final PackingPropertyContext packingProperty() throws RecognitionException {
		PackingPropertyContext _localctx = new PackingPropertyContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_packingProperty);
		try {
			setState(246);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__36:
				_localctx = new PackingMethodPropContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(209);
				match(T__36);
				setState(210);
				match(T__4);
				setState(211);
				packingMethod();
				setState(212);
				match(T__5);
				}
				break;
			case T__37:
				_localctx = new PackingGravityContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(214);
				match(T__37);
				setState(215);
				match(T__4);
				setState(216);
				match(NUMBER);
				setState(217);
				match(UNIT);
				setState(218);
				match(T__5);
				}
				break;
			case T__38:
				_localctx = new PackingSubstepsContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(219);
				match(T__38);
				setState(220);
				match(T__4);
				setState(221);
				match(NUMBER);
				setState(222);
				match(T__5);
				}
				break;
			case T__39:
				_localctx = new PackingIterationsContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(223);
				match(T__39);
				setState(224);
				match(T__4);
				setState(225);
				match(NUMBER);
				setState(226);
				match(T__5);
				}
				break;
			case T__40:
				_localctx = new PackingDampingContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(227);
				match(T__40);
				setState(228);
				match(T__4);
				setState(229);
				match(NUMBER);
				setState(230);
				match(T__5);
				}
				break;
			case T__41:
				_localctx = new PackingRestVelocityContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(231);
				match(T__41);
				setState(232);
				match(T__4);
				setState(233);
				match(NUMBER);
				setState(234);
				match(UNIT);
				setState(235);
				match(T__5);
				}
				break;
			case T__42:
				_localctx = new PackingMaxTimeContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(236);
				match(T__42);
				setState(237);
				match(T__4);
				setState(238);
				match(NUMBER);
				setState(239);
				match(UNIT);
				setState(240);
				match(T__5);
				}
				break;
			case T__43:
				_localctx = new PackingCollisionMarginContext(_localctx);
				enterOuterAlt(_localctx, 8);
				{
				setState(241);
				match(T__43);
				setState(242);
				match(T__4);
				setState(243);
				match(NUMBER);
				setState(244);
				match(UNIT);
				setState(245);
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
		enterRule(_localctx, 24, RULE_packingMethod);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(248);
			_la = _input.LA(1);
			if ( !(_la==T__44 || _la==STRING) ) {
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
		enterRule(_localctx, 26, RULE_exportSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(250);
			match(T__45);
			setState(251);
			match(T__1);
			setState(253); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(252);
				exportProperty();
				}
				}
				setState(255); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__46) | (1L << T__49) | (1L << T__50) | (1L << T__51) | (1L << T__52) | (1L << T__53) | (1L << T__54))) != 0) );
			setState(257);
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
		enterRule(_localctx, 28, RULE_exportProperty);
		try {
			setState(293);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__46:
				_localctx = new ExportFormatsContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(259);
				match(T__46);
				setState(260);
				match(T__4);
				setState(261);
				match(T__47);
				setState(262);
				formatList();
				setState(263);
				match(T__48);
				setState(264);
				match(T__5);
				}
				break;
			case T__49:
				_localctx = new ExportUnitsContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(266);
				match(T__49);
				setState(267);
				match(T__4);
				setState(268);
				match(STRING);
				setState(269);
				match(T__5);
				}
				break;
			case T__50:
				_localctx = new ExportScaleContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(270);
				match(T__50);
				setState(271);
				match(T__4);
				setState(272);
				match(NUMBER);
				setState(273);
				match(T__5);
				}
				break;
			case T__51:
				_localctx = new ExportWallModeContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(274);
				match(T__51);
				setState(275);
				match(T__4);
				setState(276);
				wallMode();
				setState(277);
				match(T__5);
				}
				break;
			case T__52:
				_localctx = new ExportFluidModeContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(279);
				match(T__52);
				setState(280);
				match(T__4);
				setState(281);
				fluidMode();
				setState(282);
				match(T__5);
				}
				break;
			case T__53:
				_localctx = new ExportManifoldCheckContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(284);
				match(T__53);
				setState(285);
				match(T__4);
				setState(286);
				match(BOOLEAN);
				setState(287);
				match(T__5);
				}
				break;
			case T__54:
				_localctx = new ExportMergeDistanceContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(288);
				match(T__54);
				setState(289);
				match(T__4);
				setState(290);
				match(NUMBER);
				setState(291);
				match(UNIT);
				setState(292);
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
		enterRule(_localctx, 30, RULE_formatList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(295);
			match(STRING);
			setState(300);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==T__55) {
				{
				{
				setState(296);
				match(T__55);
				setState(297);
				match(STRING);
				}
				}
				setState(302);
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
		enterRule(_localctx, 32, RULE_wallMode);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(303);
			_la = _input.LA(1);
			if ( !(((((_la - 57)) & ~0x3f) == 0 && ((1L << (_la - 57)) & ((1L << (T__56 - 57)) | (1L << (T__57 - 57)) | (1L << (STRING - 57)))) != 0)) ) {
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
		enterRule(_localctx, 34, RULE_fluidMode);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(305);
			_la = _input.LA(1);
			if ( !(((((_la - 20)) & ~0x3f) == 0 && ((1L << (_la - 20)) & ((1L << (T__19 - 20)) | (1L << (T__58 - 20)) | (1L << (STRING - 20)))) != 0)) ) {
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
		enterRule(_localctx, 36, RULE_cfdSection);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(307);
			match(T__59);
			setState(308);
			match(T__1);
			setState(310); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(309);
				cfdProperty();
				}
				}
				setState(312); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( ((((_la - 61)) & ~0x3f) == 0 && ((1L << (_la - 61)) & ((1L << (T__60 - 61)) | (1L << (T__61 - 61)) | (1L << (T__62 - 61)) | (1L << (T__63 - 61)) | (1L << (T__64 - 61)) | (1L << (T__65 - 61)) | (1L << (T__66 - 61)))) != 0) );
			setState(314);
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
		enterRule(_localctx, 38, RULE_cfdProperty);
		try {
			setState(348);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__60:
				_localctx = new CfdRegimePropContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(316);
				match(T__60);
				setState(317);
				match(T__4);
				setState(318);
				cfdRegime();
				setState(319);
				match(T__5);
				}
				break;
			case T__61:
				_localctx = new CfdInletVelocityContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(321);
				match(T__61);
				setState(322);
				match(T__4);
				setState(323);
				match(NUMBER);
				setState(324);
				match(UNIT);
				setState(325);
				match(T__5);
				}
				break;
			case T__62:
				_localctx = new CfdFluidDensityContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(326);
				match(T__62);
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
			case T__63:
				_localctx = new CfdFluidViscosityContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(331);
				match(T__63);
				setState(332);
				match(T__4);
				setState(333);
				match(NUMBER);
				setState(334);
				match(UNIT);
				setState(335);
				match(T__5);
				}
				break;
			case T__64:
				_localctx = new CfdMaxIterationsContext(_localctx);
				enterOuterAlt(_localctx, 5);
				{
				setState(336);
				match(T__64);
				setState(337);
				match(T__4);
				setState(338);
				match(NUMBER);
				setState(339);
				match(T__5);
				}
				break;
			case T__65:
				_localctx = new CfdConvergenceCriteriaContext(_localctx);
				enterOuterAlt(_localctx, 6);
				{
				setState(340);
				match(T__65);
				setState(341);
				match(T__4);
				setState(342);
				match(NUMBER);
				setState(343);
				match(T__5);
				}
				break;
			case T__66:
				_localctx = new CfdWriteFieldsContext(_localctx);
				enterOuterAlt(_localctx, 7);
				{
				setState(344);
				match(T__66);
				setState(345);
				match(T__4);
				setState(346);
				match(BOOLEAN);
				setState(347);
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
		enterRule(_localctx, 40, RULE_cfdRegime);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(350);
			_la = _input.LA(1);
			if ( !(((((_la - 68)) & ~0x3f) == 0 && ((1L << (_la - 68)) & ((1L << (T__67 - 68)) | (1L << (T__68 - 68)) | (1L << (STRING - 68)))) != 0)) ) {
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

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3O\u0163\4\2\t\2\4"+
		"\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t"+
		"\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\3\2\6\2.\n\2\r\2\16\2/\3\2\3"+
		"\2\3\3\3\3\3\3\3\3\3\3\3\3\5\3:\n\3\3\4\3\4\3\4\6\4?\n\4\r\4\16\4@\3\4"+
		"\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3"+
		"\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\5\5b\n\5\3\6\3\6\3"+
		"\6\6\6g\n\6\r\6\16\6h\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7"+
		"\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\5\7\u0086"+
		"\n\7\3\b\3\b\3\t\3\t\3\t\6\t\u008d\n\t\r\t\16\t\u008e\3\t\3\t\3\n\3\n"+
		"\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3"+
		"\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n"+
		"\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\5\n\u00c7"+
		"\n\n\3\13\3\13\3\f\3\f\3\f\6\f\u00ce\n\f\r\f\16\f\u00cf\3\f\3\f\3\r\3"+
		"\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r"+
		"\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3"+
		"\r\5\r\u00f9\n\r\3\16\3\16\3\17\3\17\3\17\6\17\u0100\n\17\r\17\16\17\u0101"+
		"\3\17\3\17\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20"+
		"\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20"+
		"\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\5\20\u0128\n\20\3\21\3\21\3\21"+
		"\7\21\u012d\n\21\f\21\16\21\u0130\13\21\3\22\3\22\3\23\3\23\3\24\3\24"+
		"\3\24\6\24\u0139\n\24\r\24\16\24\u013a\3\24\3\24\3\25\3\25\3\25\3\25\3"+
		"\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3"+
		"\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\5"+
		"\25\u015f\n\25\3\26\3\26\3\26\2\2\27\2\4\6\b\n\f\16\20\22\24\26\30\32"+
		"\34\36 \"$&(*\2\b\4\2\24\26KK\4\2#%KK\4\2//KK\4\2;<KK\5\2\26\26==KK\4"+
		"\2FGKK\2\u0181\2-\3\2\2\2\49\3\2\2\2\6;\3\2\2\2\ba\3\2\2\2\nc\3\2\2\2"+
		"\f\u0085\3\2\2\2\16\u0087\3\2\2\2\20\u0089\3\2\2\2\22\u00c6\3\2\2\2\24"+
		"\u00c8\3\2\2\2\26\u00ca\3\2\2\2\30\u00f8\3\2\2\2\32\u00fa\3\2\2\2\34\u00fc"+
		"\3\2\2\2\36\u0127\3\2\2\2 \u0129\3\2\2\2\"\u0131\3\2\2\2$\u0133\3\2\2"+
		"\2&\u0135\3\2\2\2(\u015e\3\2\2\2*\u0160\3\2\2\2,.\5\4\3\2-,\3\2\2\2./"+
		"\3\2\2\2/-\3\2\2\2/\60\3\2\2\2\60\61\3\2\2\2\61\62\7\2\2\3\62\3\3\2\2"+
		"\2\63:\5\6\4\2\64:\5\n\6\2\65:\5\20\t\2\66:\5\26\f\2\67:\5\34\17\28:\5"+
		"&\24\29\63\3\2\2\29\64\3\2\2\29\65\3\2\2\29\66\3\2\2\29\67\3\2\2\298\3"+
		"\2\2\2:\5\3\2\2\2;<\7\3\2\2<>\7\4\2\2=?\5\b\5\2>=\3\2\2\2?@\3\2\2\2@>"+
		"\3\2\2\2@A\3\2\2\2AB\3\2\2\2BC\7\5\2\2C\7\3\2\2\2DE\7\6\2\2EF\7\7\2\2"+
		"FG\7H\2\2GH\7J\2\2Hb\7\b\2\2IJ\7\t\2\2JK\7\7\2\2KL\7H\2\2LM\7J\2\2Mb\7"+
		"\b\2\2NO\7\n\2\2OP\7\7\2\2PQ\7H\2\2QR\7J\2\2Rb\7\b\2\2ST\7\13\2\2TU\7"+
		"\7\2\2UV\7H\2\2VW\7J\2\2Wb\7\b\2\2XY\7\f\2\2YZ\7\7\2\2Z[\7K\2\2[b\7\b"+
		"\2\2\\]\7\r\2\2]^\7\7\2\2^_\7H\2\2_`\7J\2\2`b\7\b\2\2aD\3\2\2\2aI\3\2"+
		"\2\2aN\3\2\2\2aS\3\2\2\2aX\3\2\2\2a\\\3\2\2\2b\t\3\2\2\2cd\7\16\2\2df"+
		"\7\4\2\2eg\5\f\7\2fe\3\2\2\2gh\3\2\2\2hf\3\2\2\2hi\3\2\2\2ij\3\2\2\2j"+
		"k\7\5\2\2k\13\3\2\2\2lm\7\17\2\2mn\7\7\2\2no\5\16\b\2op\7\b\2\2p\u0086"+
		"\3\2\2\2qr\7\20\2\2rs\7\7\2\2st\5\16\b\2tu\7\b\2\2u\u0086\3\2\2\2vw\7"+
		"\21\2\2wx\7\7\2\2xy\7H\2\2yz\7J\2\2z\u0086\7\b\2\2{|\7\22\2\2|}\7\7\2"+
		"\2}~\7H\2\2~\177\7J\2\2\177\u0086\7\b\2\2\u0080\u0081\7\23\2\2\u0081\u0082"+
		"\7\7\2\2\u0082\u0083\7H\2\2\u0083\u0084\7J\2\2\u0084\u0086\7\b\2\2\u0085"+
		"l\3\2\2\2\u0085q\3\2\2\2\u0085v\3\2\2\2\u0085{\3\2\2\2\u0085\u0080\3\2"+
		"\2\2\u0086\r\3\2\2\2\u0087\u0088\t\2\2\2\u0088\17\3\2\2\2\u0089\u008a"+
		"\7\27\2\2\u008a\u008c\7\4\2\2\u008b\u008d\5\22\n\2\u008c\u008b\3\2\2\2"+
		"\u008d\u008e\3\2\2\2\u008e\u008c\3\2\2\2\u008e\u008f\3\2\2\2\u008f\u0090"+
		"\3\2\2\2\u0090\u0091\7\5\2\2\u0091\21\3\2\2\2\u0092\u0093\7\30\2\2\u0093"+
		"\u0094\7\7\2\2\u0094\u0095\5\24\13\2\u0095\u0096\7\b\2\2\u0096\u00c7\3"+
		"\2\2\2\u0097\u0098\7\6\2\2\u0098\u0099\7\7\2\2\u0099\u009a\7H\2\2\u009a"+
		"\u009b\7J\2\2\u009b\u00c7\7\b\2\2\u009c\u009d\7\31\2\2\u009d\u009e\7\7"+
		"\2\2\u009e\u009f\7H\2\2\u009f\u00c7\7\b\2\2\u00a0\u00a1\7\32\2\2\u00a1"+
		"\u00a2\7\7\2\2\u00a2\u00a3\7H\2\2\u00a3\u00c7\7\b\2\2\u00a4\u00a5\7\33"+
		"\2\2\u00a5\u00a6\7\7\2\2\u00a6\u00a7\7H\2\2\u00a7\u00a8\7J\2\2\u00a8\u00c7"+
		"\7\b\2\2\u00a9\u00aa\7\34\2\2\u00aa\u00ab\7\7\2\2\u00ab\u00ac\7H\2\2\u00ac"+
		"\u00ad\7J\2\2\u00ad\u00c7\7\b\2\2\u00ae\u00af\7\35\2\2\u00af\u00b0\7\7"+
		"\2\2\u00b0\u00b1\7H\2\2\u00b1\u00c7\7\b\2\2\u00b2\u00b3\7\36\2\2\u00b3"+
		"\u00b4\7\7\2\2\u00b4\u00b5\7H\2\2\u00b5\u00c7\7\b\2\2\u00b6\u00b7\7\37"+
		"\2\2\u00b7\u00b8\7\7\2\2\u00b8\u00b9\7H\2\2\u00b9\u00c7\7\b\2\2\u00ba"+
		"\u00bb\7 \2\2\u00bb\u00bc\7\7\2\2\u00bc\u00bd\7H\2\2\u00bd\u00c7\7\b\2"+
		"\2\u00be\u00bf\7!\2\2\u00bf\u00c0\7\7\2\2\u00c0\u00c1\7H\2\2\u00c1\u00c7"+
		"\7\b\2\2\u00c2\u00c3\7\"\2\2\u00c3\u00c4\7\7\2\2\u00c4\u00c5\7H\2\2\u00c5"+
		"\u00c7\7\b\2\2\u00c6\u0092\3\2\2\2\u00c6\u0097\3\2\2\2\u00c6\u009c\3\2"+
		"\2\2\u00c6\u00a0\3\2\2\2\u00c6\u00a4\3\2\2\2\u00c6\u00a9\3\2\2\2\u00c6"+
		"\u00ae\3\2\2\2\u00c6\u00b2\3\2\2\2\u00c6\u00b6\3\2\2\2\u00c6\u00ba\3\2"+
		"\2\2\u00c6\u00be\3\2\2\2\u00c6\u00c2\3\2\2\2\u00c7\23\3\2\2\2\u00c8\u00c9"+
		"\t\3\2\2\u00c9\25\3\2\2\2\u00ca\u00cb\7&\2\2\u00cb\u00cd\7\4\2\2\u00cc"+
		"\u00ce\5\30\r\2\u00cd\u00cc\3\2\2\2\u00ce\u00cf\3\2\2\2\u00cf\u00cd\3"+
		"\2\2\2\u00cf\u00d0\3\2\2\2\u00d0\u00d1\3\2\2\2\u00d1\u00d2\7\5\2\2\u00d2"+
		"\27\3\2\2\2\u00d3\u00d4\7\'\2\2\u00d4\u00d5\7\7\2\2\u00d5\u00d6\5\32\16"+
		"\2\u00d6\u00d7\7\b\2\2\u00d7\u00f9\3\2\2\2\u00d8\u00d9\7(\2\2\u00d9\u00da"+
		"\7\7\2\2\u00da\u00db\7H\2\2\u00db\u00dc\7J\2\2\u00dc\u00f9\7\b\2\2\u00dd"+
		"\u00de\7)\2\2\u00de\u00df\7\7\2\2\u00df\u00e0\7H\2\2\u00e0\u00f9\7\b\2"+
		"\2\u00e1\u00e2\7*\2\2\u00e2\u00e3\7\7\2\2\u00e3\u00e4\7H\2\2\u00e4\u00f9"+
		"\7\b\2\2\u00e5\u00e6\7+\2\2\u00e6\u00e7\7\7\2\2\u00e7\u00e8\7H\2\2\u00e8"+
		"\u00f9\7\b\2\2\u00e9\u00ea\7,\2\2\u00ea\u00eb\7\7\2\2\u00eb\u00ec\7H\2"+
		"\2\u00ec\u00ed\7J\2\2\u00ed\u00f9\7\b\2\2\u00ee\u00ef\7-\2\2\u00ef\u00f0"+
		"\7\7\2\2\u00f0\u00f1\7H\2\2\u00f1\u00f2\7J\2\2\u00f2\u00f9\7\b\2\2\u00f3"+
		"\u00f4\7.\2\2\u00f4\u00f5\7\7\2\2\u00f5\u00f6\7H\2\2\u00f6\u00f7\7J\2"+
		"\2\u00f7\u00f9\7\b\2\2\u00f8\u00d3\3\2\2\2\u00f8\u00d8\3\2\2\2\u00f8\u00dd"+
		"\3\2\2\2\u00f8\u00e1\3\2\2\2\u00f8\u00e5\3\2\2\2\u00f8\u00e9\3\2\2\2\u00f8"+
		"\u00ee\3\2\2\2\u00f8\u00f3\3\2\2\2\u00f9\31\3\2\2\2\u00fa\u00fb\t\4\2"+
		"\2\u00fb\33\3\2\2\2\u00fc\u00fd\7\60\2\2\u00fd\u00ff\7\4\2\2\u00fe\u0100"+
		"\5\36\20\2\u00ff\u00fe\3\2\2\2\u0100\u0101\3\2\2\2\u0101\u00ff\3\2\2\2"+
		"\u0101\u0102\3\2\2\2\u0102\u0103\3\2\2\2\u0103\u0104\7\5\2\2\u0104\35"+
		"\3\2\2\2\u0105\u0106\7\61\2\2\u0106\u0107\7\7\2\2\u0107\u0108\7\62\2\2"+
		"\u0108\u0109\5 \21\2\u0109\u010a\7\63\2\2\u010a\u010b\7\b\2\2\u010b\u0128"+
		"\3\2\2\2\u010c\u010d\7\64\2\2\u010d\u010e\7\7\2\2\u010e\u010f\7K\2\2\u010f"+
		"\u0128\7\b\2\2\u0110\u0111\7\65\2\2\u0111\u0112\7\7\2\2\u0112\u0113\7"+
		"H\2\2\u0113\u0128\7\b\2\2\u0114\u0115\7\66\2\2\u0115\u0116\7\7\2\2\u0116"+
		"\u0117\5\"\22\2\u0117\u0118\7\b\2\2\u0118\u0128\3\2\2\2\u0119\u011a\7"+
		"\67\2\2\u011a\u011b\7\7\2\2\u011b\u011c\5$\23\2\u011c\u011d\7\b\2\2\u011d"+
		"\u0128\3\2\2\2\u011e\u011f\78\2\2\u011f\u0120\7\7\2\2\u0120\u0121\7L\2"+
		"\2\u0121\u0128\7\b\2\2\u0122\u0123\79\2\2\u0123\u0124\7\7\2\2\u0124\u0125"+
		"\7H\2\2\u0125\u0126\7J\2\2\u0126\u0128\7\b\2\2\u0127\u0105\3\2\2\2\u0127"+
		"\u010c\3\2\2\2\u0127\u0110\3\2\2\2\u0127\u0114\3\2\2\2\u0127\u0119\3\2"+
		"\2\2\u0127\u011e\3\2\2\2\u0127\u0122\3\2\2\2\u0128\37\3\2\2\2\u0129\u012e"+
		"\7K\2\2\u012a\u012b\7:\2\2\u012b\u012d\7K\2\2\u012c\u012a\3\2\2\2\u012d"+
		"\u0130\3\2\2\2\u012e\u012c\3\2\2\2\u012e\u012f\3\2\2\2\u012f!\3\2\2\2"+
		"\u0130\u012e\3\2\2\2\u0131\u0132\t\5\2\2\u0132#\3\2\2\2\u0133\u0134\t"+
		"\6\2\2\u0134%\3\2\2\2\u0135\u0136\7>\2\2\u0136\u0138\7\4\2\2\u0137\u0139"+
		"\5(\25\2\u0138\u0137\3\2\2\2\u0139\u013a\3\2\2\2\u013a\u0138\3\2\2\2\u013a"+
		"\u013b\3\2\2\2\u013b\u013c\3\2\2\2\u013c\u013d\7\5\2\2\u013d\'\3\2\2\2"+
		"\u013e\u013f\7?\2\2\u013f\u0140\7\7\2\2\u0140\u0141\5*\26\2\u0141\u0142"+
		"\7\b\2\2\u0142\u015f\3\2\2\2\u0143\u0144\7@\2\2\u0144\u0145\7\7\2\2\u0145"+
		"\u0146\7H\2\2\u0146\u0147\7J\2\2\u0147\u015f\7\b\2\2\u0148\u0149\7A\2"+
		"\2\u0149\u014a\7\7\2\2\u014a\u014b\7H\2\2\u014b\u014c\7J\2\2\u014c\u015f"+
		"\7\b\2\2\u014d\u014e\7B\2\2\u014e\u014f\7\7\2\2\u014f\u0150\7H\2\2\u0150"+
		"\u0151\7J\2\2\u0151\u015f\7\b\2\2\u0152\u0153\7C\2\2\u0153\u0154\7\7\2"+
		"\2\u0154\u0155\7H\2\2\u0155\u015f\7\b\2\2\u0156\u0157\7D\2\2\u0157\u0158"+
		"\7\7\2\2\u0158\u0159\7H\2\2\u0159\u015f\7\b\2\2\u015a\u015b\7E\2\2\u015b"+
		"\u015c\7\7\2\2\u015c\u015d\7L\2\2\u015d\u015f\7\b\2\2\u015e\u013e\3\2"+
		"\2\2\u015e\u0143\3\2\2\2\u015e\u0148\3\2\2\2\u015e\u014d\3\2\2\2\u015e"+
		"\u0152\3\2\2\2\u015e\u0156\3\2\2\2\u015e\u015a\3\2\2\2\u015f)\3\2\2\2"+
		"\u0160\u0161\t\7\2\2\u0161+\3\2\2\2\21/9@ah\u0085\u008e\u00c6\u00cf\u00f8"+
		"\u0101\u0127\u012e\u013a\u015e";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}