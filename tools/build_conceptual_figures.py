from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / 'generated_figures'
OUT.mkdir(parents=True, exist_ok=True)

def box(ax, x,y,w,h,text,fs=11,lw=1.4):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',facecolor='white',edgecolor='black',linewidth=lw)
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,wrap=True)
    return p

def arrow(ax,x1,y1,x2,y2,style='-|>',lw=1.2,ls='-'):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,mutation_scale=13,linewidth=lw,linestyle=ls,color='black'))

def fig_structure():
    """Copy the canonical manuscript Figure 1 assets into generated_figures.

    Figure 1 is maintained as a hand-authored SVG plus synchronized PDF/PNG
    exports in figures/. This avoids silently regenerating a visually different
    structural diagram from matplotlib.
    """
    import shutil
    src = Path(__file__).resolve().parents[1] / 'figures'
    for ext in ['svg', 'pdf', 'png']:
        shutil.copy2(src / f'figure1_structural_rank_transport.{ext}', OUT / f'figure1_structural_rank_transport.{ext}')

def fig_symmetric():
    fig,ax=plt.subplots(figsize=(11.4,5.2))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    ax.text(.5,.94,'Symmetrical evidence rule for cross-design intervention ordering',ha='center',fontsize=17,fontweight='bold')
    box(ax,.34,.77,.32,.11,'Direct contrast estimated in both assessment designs',fs=12)
    box(ax,.32,.58,.36,.11,'Evaluate each direction with uncertainty\n(CI and/or prespecified directional test)',fs=11)
    arrow(ax,.50,.77,.50,.69)
    # Three outcome columns
    box(ax,.04,.29,.28,.18,'Opposite signs\n+ both required directions supported\n\nPopulation reversal supported',fs=10.8)
    box(ax,.36,.29,.28,.18,'Same direction\n+ same ordering supported in both\n\nPopulation preservation supported',fs=10.8)
    box(ax,.68,.29,.28,.18,'Any required direction unsupported\n\nObserved sign pattern / inconclusive\n(no preservation by non-rejection)',fs=10.4)
    arrow(ax,.50,.58,.18,.47); arrow(ax,.50,.58,.50,.47); arrow(ax,.50,.58,.82,.47)
    box(ax,.20,.08,.60,.10,'Same evidential standard in both directions',fs=12)
    arrow(ax,.18,.29,.34,.18); arrow(ax,.50,.29,.50,.18); arrow(ax,.82,.29,.66,.18)
    ax.text(.5,.015,'An interaction alone does not prove strict reversal; failure to detect reversal does not prove preservation.',ha='center',va='bottom',fontsize=10.3,fontstyle='italic')
    for ext in ['pdf','png']:
        fig.savefig(OUT/f'figure2_symmetrical_evidence_rule.{ext}',bbox_inches='tight',dpi=300)
    plt.close(fig)

if __name__=='__main__':
    fig_structure(); fig_symmetric()
