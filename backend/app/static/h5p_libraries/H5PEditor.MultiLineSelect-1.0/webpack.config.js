const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = (env, argv) => {
  const isDev = argv.mode !== "production";
  const config = {
    mode: argv.mode,
    context: path.resolve(__dirname, 'src'),
    entry: {
      dist: './app.js',
    },
    devtool: isDev ? 'inline-source-map' : undefined,
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'multilineselect.js',
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          include: path.resolve(__dirname, 'src'),
          loader: 'babel-loader'
        },
        {
          test: /\.(sa|sc|c)ss$/i,
          include: path.resolve(__dirname, 'src'),
          use: [
            {
              loader: isDev ? 'style-loader' : MiniCssExtractPlugin.loader
            },
            {
              loader: 'css-loader',
              options: {
                sourceMap: true
              }
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true
              }
            }
          ]
        },
        {
          test: /\.(png|woff|woff2|eot|ttf|svg|gif)$/,
          include: path.resolve(__dirname, 'src'),
          use: [{
            loader: 'url-loader',
            options: {
              limit: 1_000_000,
            },
          }],
        },
      ],
    },
    plugins: []
  };
  if (!isDev) {
    config.plugins.push(new MiniCssExtractPlugin({ filename: 'h5p-editor-multiline-select.css' }));
  }
  return config;
};
