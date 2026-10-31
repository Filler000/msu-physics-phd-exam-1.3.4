"""Geometric sketch only: S-shaped I(V) sheet extruded along U.

This is an illustration of the user's specified slow/fast path, not an ODE
solution. Coordinates in the rendered image are an orthographic projection
of (i,u,v); v increases vertically downward. The profile is parametrised as
i=s^3-3*s, v=1.3*tanh(1.6*s). Flattened outer branches clarify the lecture
geometry. Both fast jumps have exactly constant i and u.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import FancyArrowPatch


def draw_diode(output_dir):
    OUT=Path(output_dir)
    OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":13,
                         "svg.fonttype":"none"})
    
    def current(s): return s**3-3*s
    def voltage(s): return 1.3*np.tanh(1.6*s)
    def project(i,u,v):
        return np.array([.90*np.asarray(i)+.70*np.asarray(u),
                         -2.4*np.asarray(v)+.34*np.asarray(u)-.10*np.asarray(i)])
    
    fig,ax=plt.subplots(figsize=(12.4,9.4))
    fig.patch.set_facecolor("white")
    ax.set_aspect("equal")
    ax.axis("off")
    umin,umax=-2.6,2.6
    blue="#175c91"; orange="#c75128"; border="#647d8c"
    
    # Every cross-section is the identical curve translated along U.
    # Render the three connected parts as strips without diagonal seams.
    for a,b,color in [(1,2.35,"#a9c7d7"),(-1,1,"#d5e0e5"),(-2.35,-1,"#bcd7e7")]:
        ss=np.linspace(a,b,240)
        vertices=[]
        for s0,s1 in zip(ss[:-1],ss[1:]):
            vertices.append(np.column_stack([
                project(current(s0),umin,voltage(s0)),
                project(current(s1),umin,voltage(s1)),
                project(current(s1),umax,voltage(s1)),
                project(current(s0),umax,voltage(s0))]).T)
        ax.add_collection(PolyCollection(vertices,facecolors=color,
                                        edgecolors="none",alpha=.50,zorder=1))
    
    ss=np.linspace(-2.35,2.35,1200)
    for u in [umin,-1.3,0,1.3,umax]:
        xy=project(current(ss),u,voltage(ss))
        ax.plot(*xy,color=border,lw=1.35 if u in [umin,umax] else .6,
                alpha=.85 if u in [umin,umax] else .24,zorder=2)
    for s in [-2.35,2.35]:
        xy=project(current(s),np.array([umin,umax]),voltage(s))
        ax.plot(*xy,color=border,lw=1.25,alpha=.8,zorder=2)
    for s in [-1.,1.]:
        xy=project(current(s),np.array([umin,umax]),voltage(s))
        ax.plot(*xy,color="#4e6979",lw=1.15,ls=(0,(5,4)),alpha=.72,zorder=3)
    
    # Upper repelling spiral, on the actual upper branch of the same sheet.
    upper_s=np.linspace(-2.35,-1,20000)
    upper_i=current(upper_s)
    def upper_v(i):
        return np.interp(i,upper_i,voltage(upper_s))
    t=np.linspace(0,1,1600)
    theta=-6*np.pi*(1-t)
    radius=.22+3.78*t**1.18
    i=-2+radius*np.cos(theta)
    u=-.15+.53*radius*np.sin(theta)
    v=upper_v(i)
    spiral=project(i,u,v)
    ax.plot(*spiral,color=blue,lw=2.4,zorder=6)
    
    def arrow_on(xy,k,span=18,color=blue,lw=2.0):
        ax.add_patch(FancyArrowPatch(xy[:,k],xy[:,k+span],
                     arrowstyle="-|>",mutation_scale=17,lw=lw,color=color,zorder=7))
    for k in [460,960,1360]:
        arrow_on(spiral,k)
    
    # Fast downward jump: only V varies.
    down=project(np.array([2.,2.]),np.array([-.15,-.15]),
                 voltage(np.array([-1.,2.])))
    ax.plot(*down,color=orange,lw=2.7,zorder=8)
    ax.add_patch(FancyArrowPatch(down[:,0],down[:,1],arrowstyle="-|>",
                 mutation_scale=21,lw=2.7,color=orange,zorder=8))
    
    # Slow movement along the lower outer branch, decreasing I, then its fold.
    s=np.linspace(2,1,650)
    p=np.linspace(0,1,len(s))
    lower=project(current(s),-.15+.45*(3*p*p-2*p*p*p),voltage(s))
    ax.plot(*lower,color=blue,lw=2.4,zorder=6)
    for k in [170,400]: arrow_on(lower,k,span=25)
    
    # Fast return: again exactly constant I and U, and V decreases.
    up=project(np.array([-2.,-2.]),np.array([.30,.30]),
               voltage(np.array([1.,-2.])))
    ax.add_patch(FancyArrowPatch(up[:,0],up[:,1],arrowstyle="-|>",
                 mutation_scale=21,lw=2.7,color=orange,zorder=8))
    ax.scatter(*up[:,1],s=40,color=orange,edgecolor="white",linewidth=.7,zorder=9)
    center=project(-2,-.15,voltage(-2))
    ax.scatter(*center,s=35,marker="+",linewidths=1.4,color=blue,zorder=9)
    
    # Axes are drawn outside the sheet to keep the geometry unobstructed.
    origin=np.array([-6.1,-4.25])
    for delta,label in [(np.array([2.1,-.23]),"$i$"),
                        (np.array([1.45,.70]),"$u$"),
                        (np.array([0.,-1.05]),"$v$")]:
        end=origin+delta
        ax.add_patch(FancyArrowPatch(origin,end,arrowstyle="-|>",
                    color="#394d59",lw=1.25,mutation_scale=14,zorder=10))
        offset=np.array([.15,0.]) if label!="$v$" else np.array([.12,-.12])
        ax.text(*(end+offset),label,fontsize=17,color="#263e4d",ha="left",va="center")
    
    # Compact labels; the full explanation is in the surrounding ticket text.
    def label(text,xy,textxy,color="#263e4d",align="left"):
        ax.annotate(text,xy=xy,xytext=textxy,fontsize=12.8,color=color,ha=align,
                    va="center",linespacing=1.4,
                    arrowprops={"arrowstyle":"-","color":"#8094a0","lw":.9},
                    bbox={"boxstyle":"round,pad=.25","fc":"white","ec":"none","alpha":.95},
                    zorder=12)
    label("Расходящаяся спираль",spiral[:,950],[-6.0,4.6])
    label("Скачок $+v$",down[:,0]*.50+down[:,1]*.50,[4.45,.6],
          color=orange)
    label("$i$ уменьшается",lower[:,270],[1.1,-4.5])
    label("Скачок $-v$",up[:,0]*.50+up[:,1]*.50,[-6.2,-.7],
          color=orange)

    ax.set_xlim(-7.5,8.1); ax.set_ylim(-5.7,5.1)
    fig.subplots_adjust(left=.025,right=.985,bottom=.025,top=.985)
    # At the final document width the annotations are 8.5 pt, below body text.
    scale=4.4/12.4
    for artist in fig.findobj(match=matplotlib.text.Text):
        artist.set_fontsize(8.5)
    for artist in ax.texts:
        text=artist.get_text()
        if text in ("$i$", "$u$", "$v$"):
            artist.set_fontsize(9.5)
    for artist in ax.lines:
        artist.set_linewidth(artist.get_linewidth()*scale)
    for artist in ax.patches:
        artist.set_linewidth(artist.get_linewidth()*scale)
        if isinstance(artist,FancyArrowPatch):
            artist.set_mutation_scale(artist.get_mutation_scale()*scale)
    for artist in ax.collections:
        artist.set_linewidths(artist.get_linewidths()*scale)
        if hasattr(artist,"get_sizes"):
            artist.set_sizes(artist.get_sizes()*scale**2)
    fig.set_size_inches(4.4,4.4*10.8/15.6)
    fig.savefig(OUT/"diode_chaos.pdf",facecolor="white")
    plt.close(fig)
    
    # Verify that both jumps are exactly vertical in the chosen 3D projection.
    assert np.isclose(down[0,0],down[0,1])
    assert np.isclose(up[0,0],up[0,1])
    assert np.all(np.diff(current(s))<=1e-10)
    print(OUT/"diode_chaos.pdf")


def draw_lorenz(output_dir):
    """Same ODE, initial state, sampling and view; smaller figure lettering."""
    from scipy.integrate import solve_ivp
    with plt.rc_context({"font.family":"DejaVu Sans","font.size":9,
                         "axes.titlesize":10.8,"axes.labelsize":9,
                         "xtick.labelsize":9,"ytick.labelsize":9,
                         "axes.grid":True,"grid.alpha":.25,"pdf.fonttype":42}):
        sol=solve_ivp(
            lambda t,y:[10*(y[1]-y[0]),28*y[0]-y[1]-y[0]*y[2],
                        y[0]*y[1]-8*y[2]/3],
            [0,55],[1,1,1],t_eval=np.linspace(5,55,18000),
            rtol=1e-9,atol=1e-11)
        fig=plt.figure(figsize=(5.5,3))
        ax=fig.add_subplot(111,projection="3d")
        ax.plot(*sol.y,lw=.28,color="#235d80")
        ax.set(xlabel="x",ylabel="y",zlabel="z",
               title="Система Лоренца: σ=10, b=8/3, r=28")
        ax.view_init(22,-62)
        ax.set_xticks([-20,-10,0,10,20])
        ax.set_yticks([-20,-10,0,10,20])
        ax.set_zticks([10,20,30,40])
        # Keep the previous crop and hence the trajectory's printed size.
        fig.canvas.draw()
        bbox=fig.get_tightbbox(fig.canvas.get_renderer()).padded(.1)
        ax.tick_params(axis="both",labelsize=8)
        ax.zaxis.set_tick_params(labelsize=8)
        for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
            axis.label.set_size(8.5)
        ax.set_zlabel("z",labelpad=1)
        ax.set_title("Система Лоренца: σ=10, b=8/3, r=28",fontsize=9)
        target=Path(output_dir)/"lorenz.pdf"
        fig.savefig(target,bbox_inches=bbox)
        plt.close(fig)
        print(target)


if __name__=="__main__":
    destination=Path(__file__).resolve().parents[1]/"figures"
    draw_diode(destination)
    draw_lorenz(destination)
