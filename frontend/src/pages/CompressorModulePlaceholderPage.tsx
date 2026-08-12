import { useParams } from "react-router";

type CompressorModulePlaceholderPageProps = {
  title: string;
};

export function CompressorModulePlaceholderPage({
  title,
}: CompressorModulePlaceholderPageProps) {
  const { projectId } = useParams();

  return (
    <main>
      <h1>{title}</h1>

      <p>
        Project ID: {projectId}
      </p>

      <p>
        This engineering module will be connected to the backend calculation engine next.
      </p>
    </main>
  );
}
