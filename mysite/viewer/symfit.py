# Other libraries
import numpy as np
import lmfit as lsq

# Models
from .models import Molecule

# Other imports
from .symprobabilities import *

# Symmetrical model
def sym_model(
    q,      # independant
    Vc,     # chain_volume
    Vh,     # headgroup_volume
    Vt,     # terminal_methyl_volume
    Vw,     # water_volume
    Al,     # area_per_lipid
    Dh,     # headgroup_thickness
    sig,    # smearing factor
    bc,     # chain_b
    bh,     # headgroup_b
    bt,     # terminal_methyl_b
    bw,     # water_b
    scale,  # scale
    bg      # bg
):
    return (
        (q**(-2) * scale*(
            (
                ((2*(np.exp(-((q*sig)**2)/2)))/(q*Dh*Al*Vt*Vw*(Vc-2*Vt)))
                * np.abs(
                    Vt*(bw*(Al*Dh-Vh)*(Vc-2*Vt)+Vw*bh*(Vc-2*Vt)-Vw*Al*Dh*(bc-2*bt))
                    * np.sin(q*Vc/Al) 
                    + Vt*(Vc-2*Vt)*(bw*Vh-bh*Vw)*np.sin(q*Dh+q*Vc/Al)
                    + Vw*Al*Dh*(bc*Vt-bt*Vc)*np.sin(2*q*Vt/Al)
                )
            ) **2
        ) + bg)
    )

# Symmetrical model and separated form factor
def sym_model_separated(
    q,      # independant
    Vc,     # chain_volume
    Vh,     # headgroup_volume
    Vt,     # terminal_methyl_volume
    Vw,     # water_volume
    Al,     # area_per_lipid
    Dh,     # headgroup_thickness
    sig,    # smearing factor
    r,      # Average vesicle radius
    rs,     # Relative size polydispersity
    bc,     # chain_b
    bh,     # headgroup_b
    bt,     # terminal_methyl_b
    bw,     # water_b
    scale,  # scale
    bg      # bg
):

    return (
        q**(-2) * scale * (
            (4 * 10**-8) * (
                (
                    (8*(np.pi**2)*(r**2)*(rs**4)) * (1 + rs**-2) * (2 + rs**-2)
                ) * (
                    1 - (
                        (
                            ((1 + 4*(q**2)*(r**2)*(rs**4))**(-1 / (2*rs**2))) * (np.cos((2 + rs**-2) * np.arctan(2 * q * r * (rs**2))))
                        ) / (1 + 4*(q**2)*(r**2)*(rs**4))
                    )
                )
            ) * (
                ((2*(np.exp(-((q*sig)**2)/2)))/(q*Dh*Al*Vt*Vw*(Vc-2*Vt)))
                * np.abs(
                    Vt*(bw*(Al*Dh-Vh)*(Vc-2*Vt)+Vw*bh*(Vc-2*Vt)-Vw*Al*Dh*(bc-2*bt))
                    * np.sin(q*Vc/Al) 
                    + Vt*(Vc-2*Vt)*(bw*Vh-bh*Vw)*np.sin(q*Dh+q*Vc/Al)
                    + Vw*Al*Dh*(bc*Vt-bt*Vc)*np.sin(2*q*Vt/Al)
                )
            ) **2
        ) + bg
    )

# Calculate result from model for an individual dataset
def calc_sym_model(fit_parameters, q, data, sff):
    # Convert array
    q_array = np.array(q)

    ## Unpack parameters
    # Shared
    Vc = fit_parameters['chain_volume'].value
    Vh = fit_parameters['headgroup_volume'].value
    Vt = fit_parameters['terminal_methyl_volume'].value
    # Unknown
    Al = fit_parameters['area_per_lipid'].value
    Dh = fit_parameters['headgroup_thickness'].value
    # Smearing factor
    sig = fit_parameters['sigma'].value
    # Separated form factor
    r = fit_parameters['average_vesicle_radius'].value
    rs = fit_parameters['relative_size'].value
    # Per dataset
    bc = fit_parameters['chain_b_%i' % data.id].value
    bh = fit_parameters['headgroup_b_%i' % data.id].value
    bt = fit_parameters['terminal_methyl_b_%i' % data.id].value
    bw = fit_parameters['water_b_%i' % data.id].value
    Vw = fit_parameters['combined_water_volume_%i' % data.id].value
    # Tweaks
    scale = fit_parameters['scale_%i' % data.id].value
    bg = fit_parameters['background_%i' % data.id].value

    # Check if the water prob is negative - if it is, impose a penalty
    x_values = np.arange(-40, 40, 0.2)
    water_prob = water(Vc, Vh, Al, Dh, sig, x_values)

    neg_water = False
    for value in water_prob:
        if value < 0:
            neg_water = True
            break

    # Return the calculated model
    if sff:
        calc_result = sym_model_separated(q_array, Vc, Vh, Vt, Vw, Al, Dh, sig, r, rs, bc, bh, bt, bw, scale, bg)
    else:
        calc_result = sym_model(q_array, Vc, Vh, Vt, Vw, Al, Dh, sig, bc, bh, bt, bw, scale, bg)

    # Make whole result negative if water prob is neg
    if neg_water:
        return (-calc_result)
    else:
        return (calc_result)


# Objective function create a residual for each, then flatten
def symmetrical_objective_function(fit_parameters, x, datas, sff):
    # Delcare
    current_residual = []
    combined_residuals = []

    # Make an array of residuals
    for data in datas:
        # Get error
        current_error = []
        # Check for 0's
        for value in data.error_value[data.min_index:data.max_index]:
            if value == 0:
                value = 1
            
            current_error.append(value)

        # Do math
        current_residual = data.intensity_value[data.min_index:data.max_index] - calc_sym_model(fit_parameters, data.q_value[data.min_index:data.max_index], data, sff)
        # Weight for error
        weighted_residual = np.power(current_residual, 2) / np.power(current_error, 2)
        # Append
        combined_residuals.extend(weighted_residual)

    return combined_residuals

# Augments per data-set
def adjust_b_values(data, sample_lipids, water, d_water, temp):
    # Temp
    x = temp

    # Declare
    terminal_methyl_b = 0
    chain_b = 0
    headgroup_b = 0
    water_b = 0
    calculated_water_volume = 0

    # Calculate water volume
    calculated_water_volume = (
        (
            eval(d_water.total_volume_equation) * data.d2o_mol_fraction
        ) + (
            eval(water.total_volume_equation) * (1 - data.d2o_mol_fraction)
        )
    )

    if data.data_type == 'XR':
        # bw
        water_b = water.electrons

        for sample_lipid in sample_lipids:
            if sample_lipid.sample_lipid_name.project_lipid_name:
                # bt
                terminal_methyl_b = terminal_methyl_b + (sample_lipid.sample_lipid_name.project_lipid_name.tm_electrons * sample_lipid.lipid_mol_fraction)
                # bc
                chain_b = chain_b + (sample_lipid.sample_lipid_name.project_lipid_name.tg_electrons * sample_lipid.lipid_mol_fraction)
                # bh
                headgroup_b = headgroup_b + (sample_lipid.sample_lipid_name.project_lipid_name.hg_electrons * sample_lipid.lipid_mol_fraction)
            else:
                # bt
                terminal_methyl_b = terminal_methyl_b + (sample_lipid.sample_lipid_name.project_user_lipid_name.tm_electrons * sample_lipid.lipid_mol_fraction)
                # bc
                chain_b = chain_b + (sample_lipid.sample_lipid_name.project_user_lipid_name.tg_electrons * sample_lipid.lipid_mol_fraction)
                # bh
                headgroup_b = headgroup_b + (sample_lipid.sample_lipid_name.project_user_lipid_name.hg_electrons * sample_lipid.lipid_mol_fraction)
    else:
        # bw
        water_b = (d_water.scattering_length * data.d2o_mol_fraction) + (water.scattering_length * (1 - data.d2o_mol_fraction))

        for sample_lipid in sample_lipids:
            if sample_lipid.sample_lipid_name.project_lipid_name:
                if sample_lipid.sample_lipid_augment != None:
                    # bt
                    terminal_methyl_b = terminal_methyl_b + ((sample_lipid.sample_lipid_name.project_lipid_name.tm_scattering + sample_lipid.sample_lipid_augment.tmg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                    # bc
                    chain_b = chain_b + ((sample_lipid.sample_lipid_name.project_lipid_name.tg_scattering + sample_lipid.sample_lipid_augment.tg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                    # bh
                    headgroup_b = headgroup_b + ((sample_lipid.sample_lipid_name.project_lipid_name.hg_scattering + sample_lipid.sample_lipid_augment.hg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                elif sample_lipid.sample_lipid_custom_augment != None:
                    # bt
                    terminal_methyl_b = terminal_methyl_b + ((sample_lipid.sample_lipid_name.project_lipid_name.tm_scattering + sample_lipid.sample_lipid_custom_augment.tmg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                    # bc
                    chain_b = chain_b + ((sample_lipid.sample_lipid_name.project_lipid_name.tg_scattering + sample_lipid.sample_lipid_custom_augment.tg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                    # bh
                    headgroup_b = headgroup_b + ((sample_lipid.sample_lipid_name.project_lipid_name.hg_scattering + sample_lipid.sample_lipid_custom_augment.hg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                else:
                    # bt
                    terminal_methyl_b = terminal_methyl_b + (sample_lipid.sample_lipid_name.project_lipid_name.tm_scattering * sample_lipid.lipid_mol_fraction)
                    # bc
                    chain_b = chain_b + (sample_lipid.sample_lipid_name.project_lipid_name.tg_scattering * sample_lipid.lipid_mol_fraction)
                    # bh
                    headgroup_b = headgroup_b + (sample_lipid.sample_lipid_name.project_lipid_name.hg_scattering * sample_lipid.lipid_mol_fraction)
            else:
                if sample_lipid.sample_lipid_custom_augment != None:
                    # bt
                    terminal_methyl_b = terminal_methyl_b + ((sample_lipid.sample_lipid_name.project_user_lipid_name.tm_scattering + sample_lipid.sample_lipid_custom_augment.tmg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                    # bc
                    chain_b = chain_b + ((sample_lipid.sample_lipid_name.project_user_lipid_name.tg_scattering + sample_lipid.sample_lipid_custom_augment.tg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                    # bh
                    headgroup_b = headgroup_b + ((sample_lipid.sample_lipid_name.project_user_lipid_name.hg_scattering + sample_lipid.sample_lipid_custom_augment.hg_scattering_net_change) * sample_lipid.lipid_mol_fraction)
                else:
                    # bt
                    terminal_methyl_b = terminal_methyl_b + (sample_lipid.sample_lipid_name.project_user_lipid_name.tm_scattering * sample_lipid.lipid_mol_fraction)
                    # bc
                    chain_b = chain_b + (sample_lipid.sample_lipid_name.project_user_lipid_name.tg_scattering * sample_lipid.lipid_mol_fraction)
                    # bh
                    headgroup_b = headgroup_b + (sample_lipid.sample_lipid_name.project_user_lipid_name.hg_scattering * sample_lipid.lipid_mol_fraction)

    b_values = [chain_b, headgroup_b, terminal_methyl_b, water_b, calculated_water_volume]
    
    return(b_values)

# Parameters
def symmetrical_paramitize(parameter, sample_lipids, datas, temp):
    ## DELCARE
    # Other molecules
    water = Molecule.objects.get(compound_name='water')
    d_water = Molecule.objects.get(compound_name='deuterated_water')
    
    # Parameters
    fit_parameters = lsq.Parameters()
    fit_parameters.add_many(
        # Shared
        ( # Vc
            'chain_volume',
            parameter.chain_volume,
            not(parameter.chain_volume_lock),
        ),
        ( # Vh
            'headgroup_volume',
            parameter.headgroup_volume,
            not(parameter.headgroup_volume_lock),
        ),
        ( # Vt
            'terminal_methyl_volume',
            parameter.terminal_methyl_volume,
            not(parameter.terminal_methyl_volume_lock),
            parameter.terminal_methyl_volume_lowerbound,
            parameter.terminal_methyl_volume_upperbound
        ),
        # Unknown
        ( # Al
            'area_per_lipid',
            parameter.lipid_area,
            not(parameter.lipid_area_lock),
            parameter.lipid_area_lowerbound,
            parameter.lipid_area_upperbound
        ),
        ( # Dh
            'headgroup_thickness',
            parameter.headgroup_thickness,
            not(parameter.headgroup_thickness_lock),
            parameter.headgroup_thickness_lowerbound,
            parameter.headgroup_thickness_upperbound
        ),
        # Smearing factor
        ( # Sigma
            'sigma',
            parameter.sigma,
            not(parameter.sigma_lock),
            parameter.sigma_lowerbound,
            parameter.sigma_upperbound
        ),
        ## Separated form factor
        ( # Average vesicle radius
            'average_vesicle_radius',
            parameter.average_vesicle_radius,
            not(parameter.average_vesicle_radius_lock),
            parameter.average_vesicle_radius_upperbound,
            parameter.average_vesicle_radius_lowerbound
        ),
        ( # Relative size polydispersity
            'relative_size',
            parameter.relative_size,
            not(parameter.relative_size_lock),
            parameter.relative_size_upperbound,
            parameter.relative_size_lowerbound
        )
    )

    # Per dataset
    try:
        for data in datas:
            # Get values for this data
            b_values = adjust_b_values(data, sample_lipids, water, d_water, temp)

            fit_parameters.add_many(
                ( # bc
                    'chain_b_%i' % data.id,
                    b_values[0],
                    False
                ),
                ( # bh
                    'headgroup_b_%i' % data.id,
                    b_values[1],
                    False
                ),
                ( # bt
                    'terminal_methyl_b_%i' % data.id,
                    b_values[2],
                    False
                ),
                ( # bw
                    'water_b_%i' % data.id,
                    b_values[3],
                    False
                ),
                ( # Vw
                    'combined_water_volume_%i' % data.id,
                    b_values[4],
                    False
                ),
                # Tweaks
                ( # Scale
                    'scale_%i' % data.id,
                    data.scale,
                    not(data.scale_lock),
                    data.scale_lowerbound,
                    data.scale_upperbound
                ),
                ( # BG
                    'background_%i' % data.id,
                    data.background,
                    not(data.background_lock),
                    data.background_lowerbound,
                    data.background_upperbound
                )
            )
    except TypeError:
        # Get values for this data
        b_values = adjust_b_values(datas, sample_lipids, water, d_water, temp)

        fit_parameters.add_many(
            ( # bc
                'chain_b_%i' % datas.id,
                b_values[0],
                False
            ),
            ( # bh
                'headgroup_b_%i' % datas.id,
                b_values[1],
                False
            ),
            ( # bt
                'terminal_methyl_b_%i' % datas.id,
                b_values[2],
                False
            ),
            ( # bw
                'water_b_%i' % datas.id,
                b_values[3],
                False
            ),
            ( # Vw
                'combined_water_volume_%i' % datas.id,
                b_values[4],
                False
            ),
            # Tweaks
            ( # Scale
                'scale_%i' % datas.id,
                datas.scale,
                not(datas.scale_lock),
                datas.scale_lowerbound,
                datas.scale_upperbound
            ),
            ( # BG
                'background_%i' % datas.id,
                datas.background,
                not(datas.background_lock),
                datas.background_lowerbound,
                datas.background_upperbound
            )
        )

    # Constraints

    # fit_parameters.add('penalty', value=1, vary=True, min=0)
        
    # fit_parameters.add('water_prob', expr='penalty + (headgroup_volume / (2*area_per_lipid*headgroup_thickness)) * (erfc((chain_volume+area_per_lipid*(headgroup_thickness-1)) / (sqrt(2)*area_per_lipid*sigma)) + erfc((chain_volume+area_per_lipid*(headgroup_thickness+1)) / (sqrt(2)*area_per_lipid*sigma))) + ((1/2) - headgroup_volume / (2*area_per_lipid*headgroup_thickness)) * (erfc((chain_volume-area_per_lipid*1) / (sqrt(2)*area_per_lipid*sigma)) + erfc((chain_volume+area_per_lipid*1)/(sqrt(2)*area_per_lipid*sigma)))')

    return fit_parameters

# Fit / graphs / etc
def symmetrical_graph(parameter, sample_lipids, data, temp):
    # Get parameters
    fit_parameters = symmetrical_paramitize(parameter, sample_lipids, data, temp)

    # Get result
    model_result = calc_sym_model(
        fit_parameters,
        data.q_value[data.min_index:data.max_index],
        data,
        parameter.separated
    )

    return model_result

def symmetrical_fit(parameter, sample_lipids, datas, temp):
    # Get parameters
    fit_parameters = symmetrical_paramitize(parameter, sample_lipids, datas, temp)

    # Get result
    x = None

    fit_result = lsq.minimize(
        symmetrical_objective_function,
        fit_parameters,
        args=(x, datas, parameter.separated)
    )

    return fit_result

def symmetrical_sdp(parameter, head_prob, chain_prob, tm_prob, water_prob, sample_lipids, data, temp):
    # Declare
    sdp_final = []

    # Get parameters
    fit_parameters = symmetrical_paramitize(parameter, sample_lipids, data, temp)

    # Shared
    Vh = fit_parameters['headgroup_volume'].value
    Vc = fit_parameters['chain_volume'].value
    Vt = fit_parameters['terminal_methyl_volume'].value
    Vw = fit_parameters['combined_water_volume_%i' % data.id].value

    # Unpack b values
    bh = fit_parameters['headgroup_b_%i' % data.id].value
    bc = fit_parameters['chain_b_%i' % data.id].value
    bt = fit_parameters['terminal_methyl_b_%i' % data.id].value
    bw = fit_parameters['water_b_%i' % data.id].value

    if Vh == 0 or Vc == 0 or Vt == 0 or Vw == 0:
        combined_sdp = 0
        return(combined_sdp)

    # Scale probabilities
    scaled_head_prob = (np.asarray(head_prob)*(bh/Vh))
    scaled_chain_prob = (np.asarray(chain_prob)*(bc/Vc))
    scaled_tm_prob = (np.asarray(tm_prob)*(bt/Vt))
    scaled_water_prob = (np.asarray(water_prob)*(bw/Vw))

    # Add them together
    for h_value, c_value, tm_value, w_value in zip(scaled_head_prob, scaled_chain_prob, scaled_tm_prob, scaled_water_prob):
        sdp_final.append(h_value+c_value+tm_value+w_value)

    combined_sdp = [sdp_final, scaled_head_prob, scaled_chain_prob, scaled_tm_prob, scaled_water_prob]

    return(combined_sdp)