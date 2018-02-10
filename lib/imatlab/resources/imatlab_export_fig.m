function exported = imatlab_export_fig(exporter)
    % IMATLAB_EXPORT_FIG Set exporter or export figures for imatlab.
    %
    %   IMATLAB_EXPORT_FIG(exporter)
    %     where exporter is one of
    %       {'', 'fig2plotly', 'print-jpeg', 'print-png'}
    %     sets the current exporter.
    %
    %   exported = IMATLAB_EXPORT_FIG
    %     orders the current figures by number, exports and closes them, and
    %     returns a cell array of exported filenames.

    persistent set_exporter
    if isempty(set_exporter)
        set_exporter = '';
    end
    valid_exporters = {'', 'fig2plotly', 'print-png', 'print-jpeg'};

    if exist('exporter', 'var')
        if strcmp(exporter, '')
            set(0, 'defaultfigurevisible', 'on');
        else
            set(0, 'defaultfigurevisible', 'off');
        end
        if any(strcmp(exporter, valid_exporters))
            if strcmp(exporter, 'fig2plotly')
                version_delta = ...
                    str2double(strsplit(plotly_version, '.')) - [2, 2, 7];
                if version_delta(find(version_delta, 1)) < 0
                    error('imatlab:unsupportedPlotlyVersion', ...
                          'imatlab requires plotly>=2.2.7.')
                end
            end
            set_exporter = exporter;
        else
            error('imatlab:invalidExporter', ...
                  ['known exporters are ', ...
                   strjoin(cellfun(@(c) ['''', c, ''''], valid_exporters, ...
                           'UniformOutput', false), ', ')]);
        end
    else
        children = get(0, 'children');
        [~, idx] = sort([children.Number]);
        children = children(idx);
        switch set_exporter
        case ''
            exported = {};
        case 'fig2plotly'
            exported = cell(1, numel(children));
            for i = 1:numel(children)
                name = tempname('.');
                exported{i} = [name, '.html'];
                try
                    fig2plotly(children(i), 'filename', name, ...
                               'offline', true, 'open', false);
                catch me
                    warning('fig2plotly failed to export a figure');
                    rethrow(me);
                end
                close(children(i));
            end
        case 'print-png'
            exported = cell(1, numel(children));
            for i = 1:numel(children)
                name = tempname('.');
                exported{i} = [name, '.png'];
                % Use screen resolution.
                print(children(i), exported{i}, '-dpng', '-r0');
                close(children(i));
            end
        case 'print-jpeg'
            exported = cell(1, numel(children));
            for i = 1:numel(children)
                name = tempname('.');
                exported{i} = [name, '.jpg'];
                % Use screen resolution.
                print(children(i), name, '-djpeg', '-r0');
                close(children(i));
            end
        end
    end
end
