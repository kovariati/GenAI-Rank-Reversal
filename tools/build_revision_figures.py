#!/usr/bin/env python3
"""Render bounded task-contrast and fixed-point sensitivity figures.

No raw participant data are loaded. Contrasts and intervals come from the
self-contained published-summary reconstruction; the optional scale illustration
uses the explicitly archived participant-derived group means.
"""
from pathlib import Path
import argparse
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def save(fig, stem, *, dpi=300):
    fig.savefig(stem.with_suffix('.png'), dpi=dpi, bbox_inches='tight')
    fig.savefig(stem.with_suffix('.pdf'), bbox_inches='tight',
                metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)

def build(manuscript_dir=None):
    out = ROOT / 'figures'
    out.mkdir(exist_ok=True)
    d = pd.read_csv(ROOT / 'results/wong_direct_reversal_inference.csv')
    d = d[d.outcome.eq('Originality')].set_index('regime').loc[['assisted','independent']]
    if len(d) != 2 or not np.isfinite(d[['estimate','ci_low','ci_high',
             'bonferroni_family_95ci_low','bonferroni_family_95ci_high']].to_numpy()).all():
        raise ValueError('Expected two finite originality contrast records')
    fig, ax = plt.subplots(figsize=(9.8,4.8))
    y = np.array([1.,0.])
    est = d.estimate.to_numpy()
    lo = d.bonferroni_family_95ci_low.to_numpy()
    hi = d.bonferroni_family_95ci_high.to_numpy()
    ax.errorbar(est, y, xerr=np.vstack([est-lo,hi-est]), fmt='none',
                elinewidth=1.3, capsize=7,
                label='Bonferroni intervals: joint nominal 95%, four contrasts')
    ax.errorbar(est,y,xerr=np.vstack([est-d.ci_low.to_numpy(),
                   d.ci_high.to_numpy()-est]),fmt='o',elinewidth=4,capsize=0,
                markersize=7,label='Marginal 95% Welch intervals')
    ax.axvline(0,linestyle=':',linewidth=1.2)
    ax.set_yticks(y,['Task 1: stuffed-bunny\nimprovement',
                     'Task 2: vocabulary-game\ninvention'])
    ax.set_xlabel('Originality rating difference: unrestricted minus learner-first',fontsize=10)
    ax.set_xlim(-1.58,1.55)
    ax.set_ylim(-.65,1.65)
    ax.tick_params(labelsize=10)
    ax.set_title('Two task-specific originality contrasts',fontsize=16,pad=18)
    for yy,value in zip(y,est):
        ax.annotate(f'{value:+.2f}',(value,yy),xytext=(0,13),
                    textcoords='offset points',ha='center',fontsize=11)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,-.42),frameon=False,fontsize=9)
    fig.subplots_adjust(left=.25,right=.96,top=.85,bottom=.29)
    save(fig,out / 'wong_rank_reversal')

    # Fixed-point illustration; these archived means are not a new raw-data rerun.
    means = pd.read_csv(ROOT / 'results/wong_raw_group_means.csv')
    lam = np.linspace(.1,4,400)
    fig,ax=plt.subplots(figsize=(8.6,4.9))
    for outcome in ['Originality','Usefulness']:
        tab=means[means.outcome.eq(outcome)].set_index('design')
        da=tab.loc['Unrestricted ChatGPT','assisted_task_mean']-tab.loc['Learner-first AI','assisted_task_mean']
        di=tab.loc['Unrestricted ChatGPT','independent_task_mean']-tab.loc['Learner-first AI','independent_task_mean']
        if not (np.isfinite([da,di]).all() and da>0 and di<0):
            raise ValueError('Illustration requires positive Task-1 and negative Task-2 contrasts')
        ax.plot(lam,-di/(lam*da-di),label=outcome,linewidth=2)
    ax.set(xlim=(.1,4),ylim=(0,1),xlabel='Relative scale multiplier for Task 1, λ',
           ylabel='Task-1 weight at the aggregate tie, w*')
    ax.set_title('Fixed-contrast weight / scale sensitivity',fontsize=15,pad=13)
    ax.legend(frameon=False)
    fig.text(.5,.01,'Illustrative aggregation only; not a confidence region or a calibrated common outcome.',
             ha='center',fontsize=9)
    fig.subplots_adjust(bottom=.17,left=.12,top=.87,right=.97)
    save(fig,out / 'rank_robustness_region')

    fig=plt.figure(figsize=(12.8,6.4));ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
    ax.text(.065,.85,'Generative AI and Task-Specific\nIntervention Ordering',fontsize=29,
            fontweight='bold',va='top',linespacing=1.25)
    ax.text(.065,.59,'A methodological framework and secondary analysis',fontsize=18,va='top')
    ax.text(.065,.45,'Declare the task and score → audit comparison scope\n→ estimate direct contrasts → apply uncertainty and multiplicity',
            fontsize=18,va='top',linespacing=1.6)
    ax.text(.065,.22,'Wong–Qiu: bounded product-originality ratings in two tasks.\nNot general creativity, durable learning, or an isolated AI-removal effect.',
            fontsize=15,va='top',linespacing=1.5)
    ax.text(.065,.055,'C · construct     Q · task     E · elicitation     V · verification evidence',fontsize=13)
    fig.savefig(out/'graphical_abstract.png',dpi=100)
    fig.savefig(out/'graphical_abstract.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)
    social=ROOT/'.github/assets/social-preview.png';social.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(out/'graphical_abstract.png',social)
    if manuscript_dir:
        md=Path(manuscript_dir)/'figures';md.mkdir(exist_ok=True)
        shutil.copyfile(out/'wong_rank_reversal.png',md/'figure3_wong_task_specific_contrasts.png')
        shutil.copyfile(out/'rank_robustness_region.png',md/'figure4_rank_robustness.png')
    return [out/'wong_rank_reversal.png',out/'rank_robustness_region.png',out/'graphical_abstract.png']

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--manuscript-dir')
    print('\n'.join(map(str,build(ap.parse_args().manuscript_dir))))
