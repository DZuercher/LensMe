from scipy import misc
import numpy as np
from scipy import interpolate
from scipy import misc
import astropy.cosmology as cosmo
import cmath
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import tqdm
    

class nfw_halo_lens:
    def __init__(self, M_halo=200., c_halo=3., z_halo=0.5, z_source=1., nx=1020, ny=1020, frac_pos_x=0.5, frac_pos_y=0.5):
        """
        z_source: Redshift of the source
        nx: Number of pixels along 1 axis in the image
        pos: Position of the lens relative to the image
        trunc:
        """

        self.nx = nx
        self.ny = ny
        self.dx = 0.1/60./180.*np.pi #set angular resolution o 0.1 arcmin
        self.dy = self.dx * float(self.ny) / float(self.nx)
        
        ##### HALO Properties #####
        self.z_halo = z_halo  # redshift of the halo
        M = M_halo*10**15 # halo mass in Msol
        self.c = c_halo # halo concentration 

        ##### UNITS #####
        solar = 1.98855*(10.**30) # Solar mass in kg
        mpc = 3.08567758149137*(10.**22) # Mpc in m     
        c_light = 299792458. # speed of light
        G = 6.674*(10.**(-11)) # gravitational constant

        cosmology = cosmo.FlatLambdaCDM(H0=67.26, Om0=0.316)

        self.z_source = z_source 
        self.cosmology = cosmology

        print("Initialized NFW Lens Halo with:")
        print("-------------------------------------------------------------")
        print(f"Halo Mass: {M_halo} x 10^15 Msol")
        print(f"Halo Concentration: {c_halo}")
        print(f"Halo redshift: {z_halo}")
        print(f"Lens at redshift {z_halo} and source at redshift {z_source}")
        print("-------------------------------------------------------------")

        # source - lens - observer distances
        self.d_l = cosmology.comoving_distance(self.z_halo).value #In Mpc
        self.d_s = cosmology.comoving_distance(self.z_source).value
        self.d_ls = cosmology._comoving_distance_z1z2(self.z_halo, self.z_source).value

        self.rho_c = cosmology.critical_density(self.z_halo).value*1000.*mpc**3/solar
        self.r_s = (3./4.*M/self.rho_c/500./np.pi/self.c**3)**(1./3.) # Halo radius
        self.rho_0 = self.rho_c*500./3.*self.c**3/(np.log(1.+self.c)-self.c/(1.+self.c))
        self.r_500 = self.c*self.r_s
        self.R = 5.*self.r_500 # 5 times size r500 of the halo (outer edge up to where lensing considered)

        self.gamma = G/c_light**2*solar/mpc  #G/c**2 in Solar mass/Mpc units
        self.M_500 = 500.*4.*np.pi/3.*self.rho_c*self.r_500**3
        self.theta_500 = self.r_s/self.d_l*(self.c*(1.+self.z_halo))
            
        
        self.d_l_ad = self.d_l/(1.+self.z_halo)
        self.d_s_ad = self.d_s/(1.+z_source)
        self.d_ls_ad = cosmology.angular_diameter_distance_z1z2(self.z_halo,self.z_source).value
        self.Sigma_c = 1./(4.*np.pi*self.d_l_ad*self.d_ls_ad*self.gamma)*self.d_s_ad
    
        self.a = frac_pos_x*nx
        self.b = frac_pos_y*nx
        
        # Direct calculation of the deflection field
        print("Calculating deflection field")
        self.deflection_x = np.zeros((self.ny,self.nx))
        self.deflection_y = np.zeros((self.ny,self.nx))
        for i in tqdm.tqdm(range(ny)):
            for j in range(nx):
                # relative physical distance to center of halo of pixel i,j
                (self.deflection_x[i,j],self.deflection_y[i,j]) = self.calc_deflection_field(i, j)
        print("Ready for lensing :)")

    def calc_deflection_field(self, i, j):
        """Calculate the deflection angle in x and y direction given a pixel id i,j"""

        x = (j - self.a) * self.dx * self.d_l_ad / self.r_s
        y = (i - self.b) * self.dy * self.d_l_ad / self.r_s

        R = self.R / self.r_s
        r = np.sqrt(x**2. + y**2.)
        c2 = np.log(1. + R) - R / (1. + R)

        if (0. < r < R) & np.isclose(r, 1.):
            sqrt_one_rsq = cmath.sqrt(-1. + r**2.)
            sqrt_Rsq_rsq = cmath.sqrt(R**2. - r**2.)
            f = (-2. * cmath.atan(sqrt_Rsq_rsq / sqrt_one_rsq) / sqrt_one_rsq + 2. * cmath.atan(sqrt_Rsq_rsq/(R*sqrt_one_rsq))/sqrt_one_rsq+cmath.log(R+sqrt_Rsq_rsq)-cmath.log(R-sqrt_Rsq_rsq)-2.*sqrt_Rsq_rsq/(1.+R)-2.*(-R+(1.+R)*cmath.log(1.+R))/(1.+R))/r**2.
            f = f.real
        elif r == 0.:
            f = 0.
        else:
            # critical
            f = -2. * c2 / r**2.

        alpha_x = -x * f
        alpha_y = -y * f

        alpha_x = alpha_x * self.d_ls_ad / self.d_s_ad * 8. * np.pi * self.rho_0 * self.r_s**2. * self.gamma
        alpha_y = alpha_y * self.d_ls_ad / self.d_s_ad * 8. * np.pi * self.rho_0 * self.r_s**2. * self.gamma
        return (alpha_x, alpha_y)     

    def __call__(self, img, reshape=True):
        """
        Lenses an input image
        """
        img = img.astype('uint8')
        if reshape:
            img = self.reshape_image(img)

        # angular positions of the pixels
        x, y = np.meshgrid(np.arange(0, self.nx) * self.dx, np.arange(0, self.ny) * self.dy)
        
        # new angular positions
        lxs = (x - self.deflection_x).flatten(); del x
        lys = (y - self.deflection_y).flatten(); del y

        # Lens image
        image_lensed = np.zeros((self.ny, self.nx, 3), dtype='uint8')
        image_lensed[:,:,0] = interpolate.RectBivariateSpline(np.arange(0, self.ny) * self.dy, np.arange(0, self.nx) * self.dx, img[:, :, 0]).ev(lys, lxs).reshape([self.ny, self.nx])
        image_lensed[:,:,1] = interpolate.RectBivariateSpline(np.arange(0, self.ny) * self.dy, np.arange(0, self.nx) * self.dx, img[:, :, 1]).ev(lys, lxs).reshape([self.ny, self.nx])
        image_lensed[:,:,2] = interpolate.RectBivariateSpline(np.arange(0, self.ny) * self.dy, np.arange(0, self.nx) * self.dx, img[:, :, 2]).ev(lys, lxs).reshape([self.ny, self.nx])
        return image_lensed

    def reshape_image(self, image):
        """
        Rescales original image such that smaller axis has 1020 pixels.
        Afterwards the picture is squared by selecting the middle portion.
        """
        [m,n] = image[:, :, 0].shape
        k = min(m,n)
        
        # rescaling ratio (scale to 1020 pix on one side at least)
        ratio = self.nx/k
        
        m_new = int(round(m*ratio))
        n_new = int(round(n*ratio))
        
        # resizing
        resized_image = Image.fromarray(image).resize(size=(n_new, m_new))
        resized_image = np.array(resized_image, dtype='uint8')
        channel_1 = resized_image[:,:,0]
        channel_2 = resized_image[:,:,1]
        channel_3 = resized_image[:,:,2]

        # make image square
        if n == m:
            pass
        elif n == k and n != m:
            dif = abs(n_new - m_new)
            if dif % 2 == 0:
                channel_1 = channel_1[int(dif / 2):int(dif / 2 + n_new),:]
                channel_2 = channel_2[int(dif / 2):int(dif / 2 + n_new),:]
                channel_3 = channel_3[int(dif / 2):int(dif / 2 + n_new),:]
            else:
                channel_1 = channel_1[int(dif / 2 - 0.5):(m_new-int(dif / 2 - 0.5)),:]
                channel_2 = channel_2[int(dif / 2 - 0.5):(m_new-int(dif / 2 - 0.5)),:]
                channel_3 = channel_3[int(dif / 2 - 0.5):(m_new-int(dif / 2 - 0.5)),:] 
        elif m == k and n != m:
            dif = abs(m_new - n_new)
            if dif % 2 == 0:
                channel_1 = channel_1[:,int(dif / 2):int(dif / 2 + m_new)]
                channel_2 = channel_2[:,int(dif / 2):int(dif / 2 + m_new)]
                channel_3 = channel_3[:,int(dif / 2):int(dif / 2 + m_new)]
            else:
                channel_1 = channel_1[:,int(dif / 2 + 0.5):int(n_new - dif / 2 - 0.5)]  
                channel_2 = channel_2[:,int(dif / 2 + 0.5):int(n_new - dif / 2 - 0.5)]  
                channel_3 = channel_3[:,int(dif / 2 + 0.5):int(n_new - dif / 2 - 0.5)]  
                    
        # return resizes, squared image
        p = len(channel_1)
        image_lensed = np.zeros((p,p,3), dtype='uint8')
        image_lensed[:,:,0] = np.flip(channel_1, axis=0)
        image_lensed[:,:,1] = np.flip(channel_2, axis=0)
        image_lensed[:,:,2] = np.flip(channel_3, axis=0)
        return image_lensed

if __name__ == '__main__':
    halo = nfw_halo_lens()    

    # lens the example image
    img = mpimg.imread('example.jpg')
    img_lensed = halo(img)
    plt.imsave('example_lensed.jpg', img_lensed.astype('uint8'))