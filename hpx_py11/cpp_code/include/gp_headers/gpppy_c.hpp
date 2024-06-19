#ifndef GPPPY_C_H
#define GPPPY_C_H

#include <vector>
#include <string>
#include "gp_functions.hpp"

namespace gpppy
{

    struct GP_data
    {
        int n_samples;
        std::string file_path;
        std::vector<double> data;

        GP_data(const std::string &f_path, int n);
    };

    class GP
    {

    private:
        std::vector<double> _training_input;
        std::vector<double> _training_output;
        int _n_tiles;
        int _n_tile_size;

    public:
        double lengthscale;
        double vertical_lengthscale;
        double noise_variance;
        int n_regressors;
        std::vector<bool> trainable_params;

        /// Constructor
        GP(std::vector<double> input, std::vector<double> output, int n_tiles, int n_tile_size, double l, double v, double n, int n_r, std::vector<bool> trainable_bool);

        std::string repr() const;

        std::vector<double> get_training_input() const;

        std::vector<double> get_training_output() const;

        std::vector<std::vector<double>> predict(const std::vector<double> &test_data, int m_tiles, int m_tile_size);

        std::vector<double> optimize(const gpppy_hyper::Hyperparameters &hyperparams);

        double calculate_loss();
    };

}

#endif
