"""Optional figure regeneration for agents: numpy, scipy, matplotlib.
Ready-to-use PDF figures are included; this is NOT a build step.
"""
"""Для пересчёта рисунков нужны numpy, matplotlib. Готовые PDF включены в проект."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
P=Path(__file__).resolve().parents[1]/'figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
# F^2=A^2[gamma^2+(A^2-Delta)^2]; нормированные медленные переменные.
gamma=.15;F=.18;A=np.linspace(.02,F/gamma,9000)
fig,ax=plt.subplots(figsize=(6.2,3.0))
for sign in [-1,1]:
    delta=A*A+sign*np.sqrt(np.maximum(0,(F/A)**2-gamma**2))
    D=A*A-delta;det=gamma**2+D**2+2*A*A*D
    for stable in [True,False]:
        mask=(det>0)==stable
        ax.plot(np.where(mask,delta,np.nan),np.where(mask,A,np.nan),color='#174f79' if stable else '#a74328',ls='-' if stable else '--',lw=1.5)
ax.set(xlim=(-.45,1.8),ylim=(0,1.35),xlabel=r'Расстройка $\Delta$ (нормированная)',ylabel=r'Амплитуда $A$')
ax.legend(handles=[Line2D([],[],color='#174f79',label='Устойчиво'),Line2D([],[],color='#a74328',ls='--',label='Неустойчиво')],frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(P/'duffing.pdf');plt.close(fig)
# Независимое начальное состояние для каждого r; первые 1800 итераций удаляются.
r=np.linspace(2.8,4.,2200);x=np.full_like(r,.314159)
for _ in range(1800):x=r*x*(1-x)
fig,ax=plt.subplots(figsize=(6.5,2.65))
for _ in range(220):
    x=r*x*(1-x);ax.plot(r,x,',',color='#173e5b',alpha=.42,rasterized=True)
ax.set(xlim=(2.8,4),ylim=(0,1),xlabel=r'Параметр $r$',ylabel=r'$x_n$')
fig.tight_layout();fig.savefig(P/'logistic.pdf',dpi=240);plt.close(fig)
print('Созданы duffing.pdf и logistic.pdf')

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.special import j1
P=Path(__file__).resolve().parents[1]/'figures';P.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.grid':True,'grid.alpha':.25,'pdf.fonttype':42,'savefig.bbox':'tight'})
def save(name):
 temp=P/(name+'.tmp')
 plt.savefig(temp,format='pdf')
 plt.close()
 if b'%%EOF' not in temp.read_bytes()[-1024:]:raise RuntimeError('Incomplete figure: '+name)
 temp.replace(P/name)
# Threshold and saturation.
f,ax=plt.subplots(1,2,figsize=(8,2.65));d=np.linspace(-2.5,2.5,401);thr=np.sqrt(1+d*d)
ax[0].fill_between(d,thr,3,color='#cde8d3');ax[0].plot(d,thr,color='#246445');ax[0].set(xlabel=r'$\delta/\gamma$',ylabel=r'$|\kappa|/\gamma$',ylim=(0,3),title='Главный язык неустойчивости')
k=np.linspace(0,3,401);a=np.sqrt(np.sqrt(np.maximum(k*k-1,0)))
ax[1].plot(k,a,color='#246445');ax[1].axvline(1,ls='--',color='grey');ax[1].set(xlabel=r'$\kappa/\gamma$',ylabel='Стационарная амплитуда',title=r'Насыщение: $\delta=0$, $\eta=\gamma=1$');f.tight_layout();save('parametric.pdf')
f,ax=plt.subplots(1,2,figsize=(8,2.65));r=np.linspace(0,1.8,300)
ax[0].plot(r,.5*r-r**3,label=r'$\mu>0$');ax[0].plot(r,-.2*r-r**3,label=r'$\mu<0$');ax[0].axhline(0,color='grey');ax[0].set(xlabel='Амплитуда r',ylabel=r'$\dot r$',title='Мягкое возбуждение');ax[0].legend(fontsize=8)
ax[1].plot(r,-.15*r+r**3-r**5,color='#246445');ax[1].axhline(0,color='grey');ax[1].set(xlabel='Амплитуда r',ylabel=r'$\dot r$',title='Жёсткое возбуждение: три нуля');f.tight_layout();save('selfosc_energy.pdf')
f,ax=plt.subplots(figsize=(5.6,2.5));d=np.linspace(-3,3,1201);beat=np.sign(d)*np.sqrt(np.maximum(d*d-1,0));ax.plot(d,beat);ax.plot(d,d,ls='--',color='grey',label='Без воздействия');ax.axvspan(-1,1,color='#d6eadb',label='Захват');ax.set(xlabel=r'$\Delta/K$',ylabel=r'$\langle\dot\psi\rangle/K$',title='Затягивание частоты и полоса захвата');ax.legend(fontsize=8);save('locking.pdf')
f,ax=plt.subplots(1,4,figsize=(9,2.25));xs=np.linspace(-1.3,1.3,21);X,Y=np.meshgrid(xs,xs)
fields=[(Y,-X-4*Y,'Устойчивый узел'),(Y,-X-.7*Y,'Устойчивый фокус'),(Y,X,'Седло'),(Y,-X,'Центр: линейная модель')]
for a,(U,V,title) in zip(ax,fields):a.streamplot(xs,xs,U,V,density=.7,linewidth=.65,arrowsize=.8);a.set(title=title,xlabel='x',ylabel='v',aspect='equal');a.set_xticks([-1,0,1]);a.set_yticks([-1,0,1])
f.tight_layout();save('phase_portraits.pdf')
f,ax=plt.subplots(1,2,figsize=(6.3,2.5));t=np.linspace(0,2*np.pi,300)
for a in ax:a.axhline(0,color='grey',lw=.7);a.axvline(0,color='grey',lw=.7);a.set_aspect('equal')
ax[0].axvspan(-1.5,0,color='#d8eadb');ax[0].scatter([-.8,-.3,.4],[.6,-.4,.2]);ax[0].set(xlim=(-1.5,1.5),ylim=(-1.2,1.2),xlabel=r'Re $\lambda$',ylabel=r'Im $\lambda$',title='Показатели: Re λ < 0')
ax[1].fill(np.cos(t),np.sin(t),color='#d8eadb');ax[1].plot(np.cos(t),np.sin(t));ax[1].scatter([.3,.7],[.2,-.3]);ax[1].set(xlim=(-1.3,1.3),ylim=(-1.2,1.2),xlabel=r'Re $\rho$',ylabel=r'Im $\rho$',title='Мультипликаторы: |ρ| < 1');f.tight_layout();save('stability.pdf')
sol=solve_ivp(lambda t,y:[10*(y[1]-y[0]),28*y[0]-y[1]-y[0]*y[2],y[0]*y[1]-8*y[2]/3],[0,55],[1,1,1],t_eval=np.linspace(5,55,18000),rtol=1e-9,atol=1e-11)
f=plt.figure(figsize=(5.5,3));a=f.add_subplot(111,projection='3d');a.plot(*sol.y,lw=.28,color='#235d80');a.set(xlabel='x',ylabel='y',zlabel='z',title='Система Лоренца: σ=10, b=8/3, r=28');a.view_init(22,-62);save('lorenz.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.6));t=np.linspace(-5,5,500)
for z in [0,1,3]:
 width=np.sqrt(1+z*z);ax[0].plot(t,np.exp(-t*t/width**2)/width,label=f'z/|L_D|={z}')
ax[0].set(xlabel='Сопутствующее время / T₀',ylabel='Интенсивность',title='Дисперсионное расплывание');ax[0].legend(fontsize=7)
x=np.linspace(-3,3,400)
ax[1].plot(x,x*x,label='Начальная фаза');ax[1].plot(x,-x*x,label='Компенсатор');ax[1].plot(x,0*x,label='Сумма');ax[1].set(xlabel='Частотная отстройка',ylabel='Спектральная фаза',title='Принцип компрессии');ax[1].legend(fontsize=7);f.tight_layout();save('dispersion.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));k=np.linspace(-np.pi,np.pi,400)
ax[0].plot(k,2*np.abs(np.sin(k/2)));ax[0].set(xlabel='ka',ylabel='ω в единицах √(K/m)',title='Одна масса в ячейке')
a,b=1,2;disc=np.sqrt((1/a+1/b)**2-4/(a*b)*np.sin(k/2)**2)
for sign,label in [(-1,'Акустическая'),(1,'Оптическая')]:ax[1].plot(k,np.sqrt(1/a+1/b+sign*disc),label=label)
ax[1].set(xlabel='ka (период ячейки)',ylabel='ω',title='Две массы: m₂=2m₁');ax[1].legend(fontsize=7);f.tight_layout();save('bands.pdf')
f,ax=plt.subplots(figsize=(6.3,2.4));z=np.linspace(-3,3,300);w=np.sqrt(1+z*z);ax.fill_between(z,-w,w,color='#d6e5f2');ax.plot(z,w);ax.plot(z,-w);ax.set(xlabel='z/z_R',ylabel='r/w₀',title='Границы гауссова пучка по уровню интенсивности 1/e²');save('gaussian.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));x=np.linspace(-12,12,1000)
ax[0].plot(x,np.sinc(x/np.pi)**2);airy=np.ones_like(x);mask=x!=0;airy[mask]=(2*j1(x[mask])/x[mask])**2;ax[1].plot(x,airy)
for a,t in zip(ax,['Щель: sinc²','Круглая апертура: Эйри']):a.set(xlabel='Безразмерная координата',ylabel='I/I(0)',title=t)
f.tight_layout();save('diffraction.pdf')
f,ax=plt.subplots(figsize=(6.3,2.5));xi=np.linspace(0,2*np.pi,800);u=np.sin(xi)
for t in [0,.5,.9]:ax.plot(xi+t*u,u,label=f't={t}')
ax.set(xlabel='x−c₀t',ylabel='u',title='Укручение простой волны до разрыва (β=1)');ax.legend();save('shock.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));x=np.linspace(-8,8,500)
for V in [1,2]:ax[0].plot(x,V/2/np.cosh(np.sqrt(V)*x/2)**2,label=f'V={V}')
ax[0].set(xlabel='x−Vt',ylabel='u',title='Солитоны КдВ');ax[0].legend();ax[1].plot(x,4*np.arctan(np.exp(x)));ax[1].set(xlabel='x',ylabel='φ',title='Кинк синус–Гордона');f.tight_layout();save('soliton.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));w=np.linspace(-5,5,600);tau=np.linspace(-5,5,600);ax[0].plot(tau,np.exp(-np.abs(tau)));ax[0].set(xlabel='τ/τ_c',ylabel='C/σ²',title='Экспоненциальная корреляция');ax[1].plot(w,2/(1+w*w));ax[1].set(xlabel='ωτ_c',ylabel='S/(σ²τ_c)',title='Лоренцев спектр');f.tight_layout();save('noise_spectrum.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));t=np.linspace(-2*np.pi,2*np.pi,1600);M=12;z=np.sum(np.exp(1j*np.arange(M)[:,None]*t),axis=0);rng=np.random.default_rng(123);zr=np.sum(np.exp(1j*(np.arange(M)[:,None]*t+rng.uniform(0,2*np.pi,M)[:,None])),axis=0)
for a,y,title in zip(ax,[abs(z)**2/M**2,abs(zr)**2/M**2],['Согласованные фазы','Случайные постоянные фазы']):a.plot(t/(2*np.pi),y);a.set(xlabel='t/T_R',ylabel='Нормированная интенсивность',title=title,ylim=(0,1.05))
f.tight_layout();save('modelocking.pdf')
# Device diagrams are schematic, not engineering drawings.
f,ax=plt.subplots(2,1,figsize=(8,3.0));
for a in ax:a.set_axis_off();a.set_xlim(0,10);a.set_ylim(0,1)
for a,labels in zip(ax,[['Пушка','Входной\nрезонатор','Дрейф:\nгруппировка','Выходной\nрезонатор','Коллектор'],['Пушка','Замедляющая система: фазовый синхронизм','Коллектор']]):
 positions=np.linspace(.3,8.1,len(labels))
 for pos,label in zip(positions,labels):a.text(pos,.55,label,ha='center',va='center',bbox={'boxstyle':'round,pad=.35','fc':'#e0ebf2','ec':'#426780'},fontsize=8)
 a.annotate('Электронный пучок',xy=(9,.1),xytext=(.3,.1),arrowprops={'arrowstyle':'->'},fontsize=8)
ax[0].set_title('Клистрон: скорость → плотность → отдача энергии',fontsize=9)
ax[1].text(4.5,.9,'Энергия волны: → в ЛБВ; ← в ЛОВ',ha='center',fontsize=8);f.tight_layout();save('microwave_devices.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.4))
for a in ax:a.set_aspect('equal');a.set_xlim(-.3,2.7);a.set_ylim(-.4,1.4)
ax[0].arrow(0,0,2,0,width=.015,color='#37638c');ax[0].arrow(2,0,-.4,1,width=.015,color='#ad5e32');ax[0].arrow(0,0,1.6,1,width=.015,color='#2c7c50');ax[0].text(1,-.22,'kᵢ');ax[0].text(2.1,.5,'±K');ax[0].text(.5,.7,'k_d');ax[0].set_title('Векторный синхронизм',fontsize=9)
x=np.linspace(0,np.pi,300);ax[1].plot(x,np.sin(x)**2);ax[1].set_aspect('auto');ax[1].set(xlim=(0,np.pi),ylim=(0,1.1),xlabel='|κ|L',ylabel='η₁',title='Двухволновой обмен Брэгга');ax[0].axis('off');f.tight_layout();save('acoustooptic.pdf')
f,ax=plt.subplots(figsize=(6.2,2.6));theta=np.linspace(-np.pi/2,np.pi/2,1200);N=12;d=.5;theta0=.3;u=2*np.pi*d*(np.sin(theta)-np.sin(theta0));af=abs(np.sum(np.exp(1j*np.arange(N)[:,None]*u),axis=0)/N)**2;ax.plot(theta*180/np.pi,af);ax.set(xlabel='Угол, градусы',ylabel='|AF/N|²',title='Решётка: N=12, d=λ/2, θ₀≈17°');save('array.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));x=np.linspace(0,9,500)
for a in np.linspace(-.4,.4,7):ax[0].plot(x,a*np.sin(x),lw=.8)
ax[0].set(xlabel='Горизонтальное расстояние',ylabel='Отклонение от оси',title='Канал: схематические лучи')
z=np.linspace(-2,2,300);ax[1].plot(1+.12*z*z,z);ax[1].set(xlabel='Скорость звука (отн.)',ylabel='Высота от оси',title='Минимум скорости удерживает лучи');f.tight_layout();save('channels.pdf')
f,ax=plt.subplots(1,2,figsize=(7.8,2.5));t=np.linspace(-2,2,400);sig=np.exp(-t*t/.08)*np.cos(18*t);corr=np.correlate(sig,sig,mode='same');ax[0].plot(t,sig);ax[0].set(xlabel='t',ylabel='s(t)',title='Известный импульс');ax[1].plot(t,corr/max(corr));ax[1].set(xlabel='Задержка',ylabel='Нормированный отклик',title='Согласованная корреляция');f.tight_layout();save('matched.pdf')
print('Created 18 reproducible scientific figures')

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
P=Path(__file__).resolve().parents[1]/'figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.grid':True,'grid.alpha':.22,'pdf.fonttype':42,'savefig.bbox':'tight'})
def save(name):
 plt.savefig(P/name);plt.close()

# Linear force response: normalized to static displacement f/omega0^2.
r=np.linspace(.15,1.9,1500)
fig,ax=plt.subplots(1,2,figsize=(8,2.6))
for Q in [7,20]:
 den=1-r*r-1j*r/Q
 ax[0].plot(r,1/abs(den),label=f'Q={Q}')
 ax[1].plot(r,np.angle(1/den),label=f'Q={Q}')
ax[0].set(xlabel=r'$\Omega/\omega_0$',ylabel=r'$A/(F_0/k)$',title='Амплитуда');ax[0].legend(fontsize=8)
ax[1].set(xlabel=r'$\Omega/\omega_0$',ylabel=r'Запаздывание $\varphi$',title='Фаза')
ax[1].set_yticks([0,np.pi/2,np.pi],['0','π/2','π']);fig.tight_layout();save('linear_response.pdf')

# Conservative orbits and attracting VdP cycle, actual x,xdot coordinates.
fig,ax=plt.subplots(1,2,figsize=(7.6,2.8))
t=np.linspace(0,2*np.pi,500)
for a in [.5,1,1.5,2]:ax[0].plot(a*np.cos(t),-a*np.sin(t),lw=.9)
ax[0].set(title='Консервативные орбиты',xlabel='x',ylabel='v',aspect='equal')
for init,color in [([.2,0],'#247450'),([3,0],'#9e6733')]:
 sol=solve_ivp(lambda t,z:[z[1],.3*(1-z[0]**2)*z[1]-z[0]],(0,65),init,t_eval=np.linspace(0,65,4000),rtol=1e-9,atol=1e-11)
 ax[1].plot(*sol.y,lw=.8,color=color)
 ax[1].scatter(*np.array(init)[:,None],s=12,color=color)
ax[1].set(title='Ван-дер-Поль: притяжение к циклу',xlabel='x',ylabel='v',aspect='equal')
fig.tight_layout();save('limit_cycle.pdf')

# Avoided crossing for symmetric stiffness matrix [[wa^2,-g],[-g,1]].
fig,ax=plt.subplots(1,2,figsize=(8.2,2.65))
wa=np.linspace(.78,1.22,600);g=.065
disc=np.sqrt(((wa*wa-1)/2)**2+g*g)
for sign,color in [(-1,'#246445'),(1,'#245d89')]:ax[0].plot(wa,np.sqrt((wa*wa+1)/2+sign*disc),color=color)
ax[0].plot(wa,wa,'--',color='grey',lw=.7);ax[0].axhline(1,ls='--',color='grey',lw=.7)
ax[0].set(xlabel=r'$\omega_a/\omega_b$',ylabel=r'$\omega_\pm/\omega_b$',title='Нормальные и парциальные частоты')
ws=1;was=np.sqrt(1.08);t=np.linspace(0,170,3500)
ax[1].plot(t,.5*(np.cos(ws*t)+np.cos(was*t)),lw=.6,label='x₁')
ax[1].plot(t,.5*(np.cos(ws*t)-np.cos(was*t)),lw=.6,label='x₂',alpha=.75)
ax[1].set(xlabel=r'$\omega_{\rm s} t$',ylabel='Смещение / A',title='Биения при возбуждении первой массы');ax[1].legend(fontsize=8)
fig.tight_layout();save('coupled_modes.pdf')

# Absolute beating frequency: the V-shaped curve requested in the review.
fig,ax=plt.subplots(figsize=(6,2.45));d=np.linspace(-3,3,1400)
ax.plot(d,np.sqrt(np.maximum(d*d-1,0)),label='С воздействием',color='#245d89')
ax.plot(d,abs(d),'--',color='grey',label='Без воздействия')
ax.axvspan(-1,1,color='#d6eadb',label='Захват')
ax.set(xlabel=r'$\Delta/K=(\omega_g-\Omega)/K$',ylabel=r'$\Omega_{\rm б}/K$',title='Частота биений и полоса захвата');ax.legend(fontsize=8)
save('locking.pdf')
print('Created linear_response, limit_cycle, coupled_modes; revised locking')
