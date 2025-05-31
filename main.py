from Engine import Engine
from Vehicle import Vehicle

N_VEHICLES=10
DELTA_T=0.03
V_0=60
SMALL_DELTA=6
MINIMAL_DISTANCE=2
T=1.5
A=5
B=6

if __name__ == '__main__':
    engine = Engine(n_vehicles=N_VEHICLES, delta_t=DELTA_T, v_0=V_0, small_delta=SMALL_DELTA, minimal_distance=MINIMAL_DISTANCE, T=T, a=A, b=B)
    engine.run()