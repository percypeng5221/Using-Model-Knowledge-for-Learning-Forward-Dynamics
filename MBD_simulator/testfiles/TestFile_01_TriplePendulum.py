import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), os.path.pardir ) )

from numpy import eye, array, ones, zeros, pi, arange, concatenate, append, diag, linalg, linspace
# from numpy.linalg import inv, norm
from scipy.integrate import ode, odeint, solve_ivp
from scipy.spatial.transform import Rotation as R
from classes.RigidBody import RigidBody, Ground, Rod
from classes.MultiRigidBody import MultiRigidBody
from classes.RotationalJoint import RotationalJoint
from classes.SpringDamper import SpringDamper


''' ------------------------------------------------------------------------
Setup MBD system
------------------------------------------------------------------------ '''

I_grav = array([0,-9.81,0])
ground = Ground()
link1 = Rod(length=1, radius_o=0.02, radius_i=0, I_grav=I_grav)
link2 = Rod(length=1, radius_o=0.02, radius_i=0, I_grav=I_grav)
link3 = Rod(length=1, radius_o=0.02, radius_i=0, I_grav=I_grav)
joint1 = RotationalJoint(ground,link1, A_PDp=eye(3), A_SDs=eye(3), P_r_PDp=array([0,0,0]),   S_r_SDs= array([-0.5,0,0]))
joint2 = RotationalJoint(link1, link2, A_PDp=eye(3), A_SDs=eye(3), P_r_PDp=array([0.5,0,0]), S_r_SDs= array([-0.5,0,0]))
joint3 = RotationalJoint(link1, link3, A_PDp=eye(3), A_SDs=eye(3), P_r_PDp=array([0.5,0,0]), S_r_SDs= array([-0.5,0,0]))

springDamper1 = SpringDamper(link2, link3, P_r_PDp=array([0.5,0,0]), S_r_SDs=array([0.5,0,0]), K=10, D=1, d0=1)
springDamper2 = SpringDamper(ground, link1, P_r_PDp=array([1,0,0]), S_r_SDs=array([0.5,0,0]), K=100, D=15, d0=0)

# set generalized coordinate indices
joint1.qIndex = 0
joint2.qIndex = 1
joint3.qIndex = 2

pendulum = MultiRigidBody(ground=ground, springDampers=[springDamper1, springDamper2])
nq=pendulum.nq

# set initial conditions
pendulum.setJointStates( q = array([30,10,-20]) * pi/180 )


''' ------------------------------------------------------------------------
Simulate
------------------------------------------------------------------------ '''

def odefun(t,y):
    q, qDot = y[0:nq], y[nq:]
    qDDot,_ = pendulum.forwardDynamics ( q=q, qDot=qDot )
    return concatenate((qDot,qDDot))

# initial conditions
q0, dq0, ddq0  = pendulum.getJointStates()

# simulate
tf = 20
fps = 60
odesol = solve_ivp( odefun, t_span=[0,tf], t_eval=arange(0,tf,1/fps), y0=concatenate((q0,dq0)).squeeze(), method='RK45', dense_output=True, events=None )

from matplotlib import pyplot as plt
plt.figure()
plt.plot(odesol.t, odesol.y[0,:]*180/pi, label='joint1.q')
plt.plot(odesol.t, odesol.y[1,:]*180/pi, label='joint2.q')
plt.plot(odesol.t, odesol.y[2,:]*180/pi, label='joint3.q')
plt.legend()
plt.grid(True)
plt.show()


''' ------------------------------------------------------------------------
Animate
------------------------------------------------------------------------ '''

pendulum.initGraphics(width=1200, height=800, range=1.5, title='A double pendulum', updaterate=fps)

while True:
    for t,y in zip(odesol.t,odesol.y.T):
        pendulum.setJointStates( q=y[0:nq], qDot=y[nq:] )
        pendulum.forwardKinematics()
        pendulum.updateGraphics()

print('Animation finished!')
